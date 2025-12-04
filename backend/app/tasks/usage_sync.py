"""
Usage synchronization tasks
"""
from celery import shared_task
from loguru import logger
from app.core.celery_app import celery_app
from app.crud.config import config_crud
from app.crud.server import server_crud
from app.services.sui_client import SUIClient, SUIClientError


@shared_task
def sync_usage_from_sui():
    """
    Sync usage data from all S-UI panels
    Runs every 6 hours
    """
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import AsyncSessionLocal
        
        async def sync_usage():
            async with AsyncSessionLocal() as db:
                # Get all active servers
                servers = await server_crud.get_active_servers(db)
                
                for server in servers:
                    try:
                        sui_client = SUIClient(server.panel_url, server.api_key)
                        
                        # Get all usage data
                        usage_data = await sui_client.get_all_usage()
                        
                        # Update configs with usage data
                        configs = await config_crud.get_by_server(db, server.id)
                        
                        for config in configs:
                            if config.sui_client_id and config.sui_client_id in usage_data:
                                used_gb = usage_data[config.sui_client_id]
                                await config_crud.update_usage(db, config.id, used_gb)
                                logger.debug(f"Updated usage for config {config.id}: {used_gb} GB")
                        
                        logger.info(f"Synced usage for server {server.id}")
                        
                    except SUIClientError as e:
                        logger.error(f"Failed to sync usage for server {server.id}: {str(e)}")
                        continue
                    except Exception as e:
                        logger.error(f"Error syncing server {server.id}: {str(e)}")
                        continue
        
        import asyncio
        asyncio.run(sync_usage())
        
    except Exception as e:
        logger.error(f"Error in sync_usage_from_sui task: {str(e)}")


@shared_task
def sync_single_config_usage(config_id: int):
    """
    Sync usage for a single config
    
    Args:
        config_id: Config ID
    """
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import AsyncSessionLocal
        
        async def sync_single():
            async with AsyncSessionLocal() as db:
                config = await config_crud.get(db, config_id)
                if not config or not config.sui_client_id:
                    return
                
                server = await server_crud.get(db, config.server_id)
                if not server:
                    return
                
                sui_client = SUIClient(server.panel_url, server.api_key)
                
                try:
                    usage = await sui_client.get_client_usage(config.sui_client_id)
                    used_bytes = usage.get("used", 0)
                    used_gb = used_bytes / (1024 ** 3)
                    
                    await config_crud.update_usage(db, config_id, used_gb)
                    logger.info(f"Synced usage for config {config_id}: {used_gb} GB")
                    
                except SUIClientError as e:
                    logger.error(f"Failed to sync usage for config {config_id}: {str(e)}")
        
        import asyncio
        asyncio.run(sync_single())
        
    except Exception as e:
        logger.error(f"Error in sync_single_config_usage task: {str(e)}")

