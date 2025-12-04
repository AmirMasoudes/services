"""
Server schemas
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime


class ServerBase(BaseModel):
    """Base server schema"""
    name: str = Field(..., min_length=1, max_length=100)
    ip: str = Field(..., description="Server IP address")
    panel_url: str = Field(..., description="S-UI panel URL")
    api_key: str = Field(..., min_length=1, description="S-UI API key")
    max_config_limit: int = Field(100, ge=1, description="Maximum number of configs")


class ServerCreate(ServerBase):
    """Server creation schema"""
    pass


class ServerUpdate(BaseModel):
    """Server update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    ip: Optional[str] = None
    panel_url: Optional[str] = None
    api_key: Optional[str] = None
    max_config_limit: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class ServerResponse(ServerBase):
    """Server response schema"""
    id: int
    current_config_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ServerListResponse(ServerResponse):
    """Server list response with capacity info"""
    available_capacity: int
    is_full: bool

