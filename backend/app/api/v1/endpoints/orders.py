"""
Orders endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.order import order_crud
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.dependencies import get_current_user, get_current_admin
from app.models.order import OrderStatus
from app.services.notification import NotificationService
from datetime import datetime, date

router = APIRouter()


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new order
    """
    # Check if user is admin or creating for themselves
    if order_data.user_id and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create orders for other users"
        )
    
    user_id = order_data.user_id if order_data.user_id else current_user["id"]
    
    # Create order
    order_dict = order_data.model_dump()
    order_dict["user_id"] = user_id
    order = await order_crud.create(db, order_dict)
    
    # Send Telegram notification to admin
    if order.status == OrderStatus.COMPLETED:
        notification_service = NotificationService()
        await notification_service.send_order_notification(order)
    
    return order


@router.get("", response_model=PaginatedResponse[OrderListResponse])
async def get_orders(
    pagination: PaginationParams = Depends(),
    user_id: Optional[int] = Query(None),
    status_filter: Optional[OrderStatus] = Query(None, alias="status"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of orders with pagination
    """
    # Non-admins can only see their own orders
    if current_user["role"] != "admin":
        user_id = current_user["id"]
    
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if status_filter:
        filters["status"] = status_filter
    
    orders, total = await order_crud.get_multi(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
        start_date=start_date,
        end_date=end_date
    )
    
    # Add user info
    order_list = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "user_id": order.user_id,
            "plan_id": order.plan_id,
            "amount": float(order.amount),
            "profit": float(order.profit),
            "status": order.status,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "username": order.user.username if order.user else None,
        }
        order_list.append(OrderListResponse(**order_dict))
    
    return PaginatedResponse.create(order_list, total, pagination.page, pagination.page_size)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get order by ID
    """
    order = await order_crud.get_with_relations(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Non-admins can only see their own orders
    if current_user["role"] != "admin" and order.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Update order (Admin only)
    """
    order = await order_crud.get_with_relations(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    update_data = order_data.model_dump(exclude_unset=True)
    
    # Send notification if status changed to completed
    if "status" in update_data and update_data["status"] == OrderStatus.COMPLETED and order.status != OrderStatus.COMPLETED:
        updated_order = await order_crud.update(db, order, update_data)
        notification_service = NotificationService()
        await notification_service.send_order_notification(updated_order)
        return updated_order
    
    updated_order = await order_crud.update(db, order, update_data)
    return updated_order


@router.get("/stats/summary", status_code=status.HTTP_200_OK)
async def get_orders_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get orders summary statistics (Admin only)
    """
    stats = await order_crud.get_summary_stats(db, start_date, end_date)
    return stats

