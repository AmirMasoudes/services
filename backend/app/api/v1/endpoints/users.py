"""
Users endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.user import user_crud
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserBalanceUpdate,
    UserListResponse,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.dependencies import get_current_user, get_current_admin

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Create a new user (Admin only)
    """
    # Check if username exists
    existing_user = await user_crud.get_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    if user_data.email:
        existing_email = await user_crud.get_by_email(db, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    # Create user
    user_dict = user_data.model_dump()
    user = await user_crud.create(db, user_dict)
    
    return user


@router.get("", response_model=PaginatedResponse[UserListResponse])
async def get_users(
    pagination: PaginationParams = Depends(),
    role: Optional[str] = Query(None),
    is_banned: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get list of users with pagination (Admin only)
    """
    filters = {}
    if role:
        filters["role"] = role
    if is_banned:
        filters["is_banned"] = is_banned
    
    users, total = await user_crud.get_multi(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters
    )
    
    # Add stats to each user
    user_list = []
    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tg_id": user.tg_id,
            "role": user.role,
            "balance": float(user.balance),
            "is_banned": user.is_banned,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "configs_count": len(user.configs) if hasattr(user, "configs") else 0,
            "orders_count": len(user.orders) if hasattr(user, "orders") else 0,
        }
        user_list.append(UserListResponse(**user_dict))
    
    return PaginatedResponse.create(user_list, total, pagination.page, pagination.page_size)


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's profile
    """
    user = await user_crud.get(db, current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get user by ID (Admin only)
    """
    user = await user_crud.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Update user (Admin only)
    """
    user = await user_crud.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Check username uniqueness if updating
    if "username" in update_data and update_data["username"] != user.username:
        existing = await user_crud.get_by_username(db, update_data["username"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
    
    # Check email uniqueness if updating
    if "email" in update_data and update_data["email"] and update_data["email"] != user.email:
        existing = await user_crud.get_by_email(db, update_data["email"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    updated_user = await user_crud.update(db, user, update_data)
    return updated_user


@router.post("/{user_id}/balance", response_model=UserResponse)
async def update_user_balance(
    user_id: int,
    balance_data: UserBalanceUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Update user balance (Admin only)
    """
    user = await user_crud.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = await user_crud.update_balance(db, user_id, balance_data.amount)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Delete user (Admin only)
    """
    deleted = await user_crud.delete(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

