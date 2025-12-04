"""
Servers endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.server import server_crud
from app.schemas.server import (
    ServerCreate,
    ServerUpdate,
    ServerResponse,
    ServerListResponse,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.dependencies import get_current_admin
from app.services.sui_client import SUIClient, SUIClientError

router = APIRouter()


@router.post("", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(
    server_data: ServerCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Create a new server (Admin only)
    """
    # Check if IP already exists
    existing_server = await server_crud.get_by_ip(db, server_data.ip)
    if existing_server:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server with this IP already exists"
        )
    
    # Verify S-UI panel connection
    sui_client = SUIClient(server_data.panel_url, server_data.api_key)
    try:
        is_healthy = await sui_client.check_health()
        if not is_healthy:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot connect to S-UI panel. Please check panel URL and API key."
            )
    except SUIClientError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot connect to S-UI panel: {str(e)}"
        )
    
    # Create server
    server_dict = server_data.model_dump()
    server = await server_crud.create(db, server_dict)
    
    return server


@router.get("", response_model=PaginatedResponse[ServerListResponse])
async def get_servers(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get list of servers with pagination (Admin only)
    """
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    
    servers, total = await server_crud.get_multi(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters
    )
    
    # Add capacity info
    server_list = []
    for server in servers:
        server_dict = {
            "id": server.id,
            "name": server.name,
            "ip": server.ip,
            "panel_url": server.panel_url,
            "max_config_limit": server.max_config_limit,
            "current_config_count": server.current_config_count,
            "is_active": server.is_active,
            "created_at": server.created_at,
            "updated_at": server.updated_at,
            "available_capacity": server.available_capacity,
            "is_full": server.is_full,
        }
        server_list.append(ServerListResponse(**server_dict))
    
    return PaginatedResponse.create(server_list, total, pagination.page, pagination.page_size)


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get server by ID (Admin only)
    """
    server = await server_crud.get(db, server_id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    return server


@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: int,
    server_data: ServerUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Update server (Admin only)
    """
    server = await server_crud.get(db, server_id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    
    update_data = server_data.model_dump(exclude_unset=True)
    
    # Check IP uniqueness if updating
    if "ip" in update_data and update_data["ip"] != server.ip:
        existing = await server_crud.get_by_ip(db, update_data["ip"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Server with this IP already exists"
            )
    
    # Verify S-UI panel connection if URL or API key changed
    if "panel_url" in update_data or "api_key" in update_data:
        panel_url = update_data.get("panel_url", server.panel_url)
        api_key = update_data.get("api_key", server.api_key)
        sui_client = SUIClient(panel_url, api_key)
        try:
            is_healthy = await sui_client.check_health()
            if not is_healthy:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot connect to S-UI panel. Please check panel URL and API key."
                )
        except SUIClientError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot connect to S-UI panel: {str(e)}"
            )
    
    updated_server = await server_crud.update(db, server, update_data)
    return updated_server


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Delete server (Admin only)
    """
    deleted = await server_crud.delete(db, server_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )


@router.post("/{server_id}/check-health", status_code=status.HTTP_200_OK)
async def check_server_health(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Check server health (Admin only)
    """
    server = await server_crud.get(db, server_id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    
    sui_client = SUIClient(server.panel_url, server.api_key)
    try:
        is_healthy = await sui_client.check_health()
        return {"healthy": is_healthy, "server_id": server_id}
    except SUIClientError as e:
        return {"healthy": False, "server_id": server_id, "error": str(e)}


@router.get("/{server_id}/capacity", status_code=status.HTTP_200_OK)
async def get_server_capacity(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get server capacity information (Admin only)
    """
    server = await server_crud.get(db, server_id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    
    return {
        "server_id": server.id,
        "max_config_limit": server.max_config_limit,
        "current_config_count": server.current_config_count,
        "available_capacity": server.available_capacity,
        "is_full": server.is_full,
    }

