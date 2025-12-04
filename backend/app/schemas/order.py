"""
Order schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.order import OrderStatus


class OrderBase(BaseModel):
    """Base order schema"""
    plan_id: Optional[int] = None
    amount: float = Field(..., ge=0, description="Order amount")
    profit: float = Field(..., ge=0, description="Admin profit")


class OrderCreate(OrderBase):
    """Order creation schema"""
    user_id: Optional[int] = None  # Can be null for anonymous orders


class OrderUpdate(BaseModel):
    """Order update schema"""
    status: Optional[OrderStatus] = None
    amount: Optional[float] = Field(None, ge=0)
    profit: Optional[float] = Field(None, ge=0)


class OrderResponse(OrderBase):
    """Order response schema"""
    id: int
    user_id: Optional[int]
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderListResponse(OrderResponse):
    """Order list response with user info"""
    username: Optional[str] = None


class OrderStatsResponse(BaseModel):
    """Order statistics response"""
    total_orders: int
    total_income: float
    total_profit: float
    pending_orders: int
    completed_orders: int
    cancelled_orders: int
    daily_breakdown: Optional[list] = None

