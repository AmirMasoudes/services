"""
Ticket schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.ticket import TicketStatus


class TicketBase(BaseModel):
    """Base ticket schema"""
    message: str = Field(..., min_length=1, max_length=5000)


class TicketCreate(TicketBase):
    """Ticket creation schema"""
    user_id: Optional[int] = Field(None, description="User ID (current user if not provided)")


class TicketUpdate(BaseModel):
    """Ticket update schema"""
    answer: Optional[str] = Field(None, min_length=1, max_length=5000)
    status: Optional[TicketStatus] = None


class TicketResponse(TicketBase):
    """Ticket response schema"""
    id: int
    user_id: int
    answer: Optional[str] = None
    status: TicketStatus
    telegram_message_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TicketListResponse(TicketResponse):
    """Ticket list response with user info"""
    username: Optional[str] = None

