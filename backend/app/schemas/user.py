"""
User schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    tg_id: Optional[int] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    tg_id: Optional[int] = None
    role: Optional[UserRole] = None
    is_banned: Optional[str] = None  # "true" or "false"


class UserBalanceUpdate(BaseModel):
    """User balance update schema"""
    amount: float = Field(..., description="Amount to add (positive) or subtract (negative)")
    description: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: UserRole
    balance: float
    is_banned: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(UserResponse):
    """User list response with additional stats"""
    configs_count: Optional[int] = 0
    orders_count: Optional[int] = 0

