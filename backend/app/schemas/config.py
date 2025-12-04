"""
Config/Inbound schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.config import ConfigType, ConfigStatus


class ConfigBase(BaseModel):
    """Base config schema"""
    type: ConfigType
    data_limit_gb: Optional[float] = Field(None, ge=0, description="Data limit in GB, null for unlimited")
    expire_at: Optional[datetime] = None


class ConfigCreate(ConfigBase):
    """Config creation schema"""
    user_id: Optional[int] = Field(None, description="User ID (current user if not provided)")
    server_id: Optional[int] = Field(None, description="Server ID (auto-assigned if not provided)")


class ConfigUpdate(BaseModel):
    """Config update schema"""
    data_limit_gb: Optional[float] = Field(None, ge=0)
    expire_at: Optional[datetime] = None
    status: Optional[ConfigStatus] = None


class ConfigResponse(ConfigBase):
    """Config response schema"""
    id: int
    user_id: int
    server_id: int
    used_data_gb: float
    status: ConfigStatus
    sui_client_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConfigUsageUpdate(BaseModel):
    """Config usage update schema (from webhook)"""
    config_id: int
    used_data_gb: float


class ConfigListResponse(ConfigResponse):
    """Config list response with user and server info"""
    username: Optional[str] = None
    server_name: Optional[str] = None


class ConfigWebhookData(BaseModel):
    """Webhook data from S-UI panel"""
    client_id: str
    used_data_gb: float
    total_data_gb: Optional[float] = None

