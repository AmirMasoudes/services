"""
Config/Inbound model
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ConfigType(str, enum.Enum):
    """Config type enumeration"""
    VMESS = "vmess"
    VLESS = "vless"
    TROJAN = "trojan"


class ConfigStatus(str, enum.Enum):
    """Config status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"


class Config(Base):
    """Config/Inbound model"""
    __tablename__ = "configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    server_id = Column(Integer, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SQLEnum(ConfigType), nullable=False)
    data_limit_gb = Column(Numeric(10, 2), nullable=True)  # NULL = unlimited
    used_data_gb = Column(Numeric(10, 2), default=0.00, nullable=False)
    expire_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(ConfigStatus), default=ConfigStatus.ACTIVE, nullable=False, index=True)
    sui_client_id = Column(String(100), nullable=True, index=True)  # S-UI client ID
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="configs")
    server = relationship("Server", back_populates="configs")
    
    @property
    def is_expired(self) -> bool:
        """Check if config is expired"""
        if not self.expire_at:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expire_at
    
    @property
    def is_over_limit(self) -> bool:
        """Check if config exceeded data limit"""
        if not self.data_limit_gb:
            return False
        return float(self.used_data_gb) >= float(self.data_limit_gb)
    
    def __repr__(self):
        return f"<Config(id={self.id}, user_id={self.user_id}, type={self.type}, status={self.status})>"

