"""
Config/Inbound endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.config import config_crud
from app.crud.server import server_crud
from app.schemas.config import (
    ConfigCreate,
    ConfigUpdate,
    ConfigResponse,
    ConfigListResponse,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.dependencies import get_current_user, get_current_admin
from app.models.config import ConfigStatus, ConfigType
from app.services.sui_client import SUIClient, SUIClientError
from datetime import datetime, timezone

router = APIRouter()


@router.post("", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    config_data: ConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new config
    """
    # Check if user is admin or creating for themselves
    if config_data.user_id and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create configs for other users"
        )
    
    user_id = config_data.user_id if config_data.user_id else current_user["id"]
    
    # Find available server
    server = await server_crud.find_available_server(db)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No available servers. All servers are at capacity."
        )
    
    # Create config in S-UI panel
    sui_client = SUIClient(server.panel_url, server.api_key)
    
    try:
        # Generate email for S-UI client
        email = f"user_{user_id}_config_{datetime.now(timezone.utc).timestamp()}"
        
        # Create client in S-UI
        sui_client_data = await sui_client.create_client(
            email=email,
            config_type=config_data.type.value,
            data_limit_gb=float(config_data.data_limit_gb) if config_data.data_limit_gb else None,
            expire_at=config_data.expire_at.isoformat() if config_data.expire_at else None
        )
        
        sui_client_id = sui_client_data.get("id") or sui_client_data.get("client_id")
        if not sui_client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get client ID from S-UI panel"
            )
        
        # Create config in database
        config_dict = config_data.model_dump()
        config_dict["user_id"] = user_id
        config_dict["server_id"] = server.id
        config_dict["sui_client_id"] = str(sui_client_id)
        config = await config_crud.create(db, config_dict)
        
        # Update server config count
        await server_crud.increment_config_count(db, server.id)
        
        return config
        
    except SUIClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create config in S-UI panel: {str(e)}"
        )


@router.get("", response_model=PaginatedResponse[ConfigListResponse])
async def get_configs(
    pagination: PaginationParams = Depends(),
    user_id: Optional[int] = Query(None),
    server_id: Optional[int] = Query(None),
    status_filter: Optional[ConfigStatus] = Query(None, alias="status"),
    type_filter: Optional[ConfigType] = Query(None, alias="type"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of configs with pagination
    """
    # Non-admins can only see their own configs
    if current_user["role"] != "admin":
        user_id = current_user["id"]
    
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if server_id:
        filters["server_id"] = server_id
    if status_filter:
        filters["status"] = status_filter
    if type_filter:
        filters["type"] = type_filter
    
    configs, total = await config_crud.get_multi(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters
    )
    
    # Add user and server info
    config_list = []
    for config in configs:
        config_dict = {
            "id": config.id,
            "user_id": config.user_id,
            "server_id": config.server_id,
            "type": config.type,
            "data_limit_gb": float(config.data_limit_gb) if config.data_limit_gb else None,
            "used_data_gb": float(config.used_data_gb),
            "expire_at": config.expire_at,
            "status": config.status,
            "sui_client_id": config.sui_client_id,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "username": config.user.username if config.user else None,
            "server_name": config.server.name if config.server else None,
        }
        config_list.append(ConfigListResponse(**config_dict))
    
    return PaginatedResponse.create(config_list, total, pagination.page, pagination.page_size)


@router.get("/{config_id}", response_model=ConfigResponse)
async def get_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get config by ID
    """
    config = await config_crud.get_with_relations(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    # Non-admins can only see their own configs
    if current_user["role"] != "admin" and config.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return config


@router.put("/{config_id}", response_model=ConfigResponse)
async def update_config(
    config_id: int,
    config_data: ConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update config (Admin only)
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update configs"
        )
    
    config = await config_crud.get_with_relations(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    update_data = config_data.model_dump(exclude_unset=True)
    
    # Update in S-UI if needed
    if "data_limit_gb" in update_data or "expire_at" in update_data:
        server = await server_crud.get(db, config.server_id)
        if server and config.sui_client_id:
            sui_client = SUIClient(server.panel_url, server.api_key)
            try:
                if "data_limit_gb" in update_data:
                    await sui_client.update_client_limit(
                        config.sui_client_id,
                        float(update_data["data_limit_gb"]) if update_data["data_limit_gb"] else None
                    )
                if "expire_at" in update_data:
                    expire_str = update_data["expire_at"].isoformat() if update_data["expire_at"] else None
                    await sui_client.update_client_expiry(config.sui_client_id, expire_str)
            except SUIClientError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update config in S-UI panel: {str(e)}"
                )
    
    updated_config = await config_crud.update(db, config, update_data)
    return updated_config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete config
    """
    config = await config_crud.get_with_relations(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    # Non-admins can only delete their own configs
    if current_user["role"] != "admin" and config.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete from S-UI panel
    if config.sui_client_id:
        server = await server_crud.get(db, config.server_id)
        if server:
            sui_client = SUIClient(server.panel_url, server.api_key)
            try:
                await sui_client.delete_client(config.sui_client_id)
            except SUIClientError as e:
                # Log error but continue with database deletion
                pass
    
    # Delete from database
    await config_crud.delete(db, config_id)
    
    # Update server config count
    if config.server_id:
        await server_crud.decrement_config_count(db, config.server_id)

