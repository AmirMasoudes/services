"""
Config expiry and limit checking tasks
"""
from celery import shared_task
from loguru import logger
from datetime import datetime, timezone
from app.core.celery_app import celery_app
from app.crud.config import config_crud
from app.crud.server import server_crud
from app.models.config import ConfigStatus
from app.services.sui_client import SUIClient, SUIClientError


@shared_task
def check_expired_configs():
    """
    Check and disable expired configs
    Runs every hour
    """
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import AsyncSessionLocal
        
        async def process_expired():
            async with AsyncSessionLocal() as db:
                expired_configs = await config_crud.get_expired_configs(db)
                
                for config in expired_configs:
                    try:
                        # Update status to expired
                        await config_crud.update(
                            db,
                            config,
                            {"status": ConfigStatus.EXPIRED}
                        )
                        
                        # Disable in S-UI panel
                        if config.sui_client_id:
                            server = await server_crud.get(db, config.server_id)
                            if server:
                                sui_client = SUIClient(server.panel_url, server.api_key)
                                try:
                                    # Delete or disable client in S-UI
                                    await sui_client.delete_client(config.sui_client_id)
                                except SUIClientError as e:
                                    logger.error(f"Failed to disable config {config.id} in S-UI: {str(e)}")
                        
                        logger.info(f"Disabled expired config {config.id}")
                        
                    except Exception as e:
                        logger.error(f"Error processing expired config {config.id}: {str(e)}")
                        continue
        
        import asyncio
        asyncio.run(process_expired())
        
    except Exception as e:
        logger.error(f"Error in check_expired_configs task: {str(e)}")


@shared_task
def check_over_limit_configs():
    """
    Check and disable configs that exceeded data limit
    Runs every hour
    """
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import AsyncSessionLocal
        
        async def process_over_limit():
            async with AsyncSessionLocal() as db:
                over_limit_configs = await config_crud.get_over_limit_configs(db)
                
                for config in over_limit_configs:
                    try:
                        # Update status to disabled
                        await config_crud.update(
                            db,
                            config,
                            {"status": ConfigStatus.DISABLED}
                        )
                        
                        # Disable in S-UI panel
                        if config.sui_client_id:
                            server = await server_crud.get(db, config.server_id)
                            if server:
                                sui_client = SUIClient(server.panel_url, server.api_key)
                                try:
                                    await sui_client.delete_client(config.sui_client_id)
                                except SUIClientError as e:
                                    logger.error(f"Failed to disable config {config.id} in S-UI: {str(e)}")
                        
                        logger.info(f"Disabled over-limit config {config.id}")
                        
                    except Exception as e:
                        logger.error(f"Error processing over-limit config {config.id}: {str(e)}")
                        continue
        
        import asyncio
        asyncio.run(process_over_limit())
        
    except Exception as e:
        logger.error(f"Error in check_over_limit_configs task: {str(e)}")

