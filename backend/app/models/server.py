"""
Server model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Server(Base):
    """Server model representing a VPS connected to S-UI"""
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    ip = Column(String(45), nullable=False, unique=True, index=True)  # IPv6 support
    panel_url = Column(String(500), nullable=False)
    api_key = Column(String(255), nullable=False)
    max_config_limit = Column(Integer, default=100, nullable=False)
    current_config_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    configs = relationship("Config", back_populates="server", cascade="all, delete-orphan")
    
    @property
    def available_capacity(self) -> int:
        """Calculate available capacity"""
        return max(0, self.max_config_limit - self.current_config_count)
    
    @property
    def is_full(self) -> bool:
        """Check if server is at capacity"""
        return self.current_config_count >= self.max_config_limit
    
    def __repr__(self):
        return f"<Server(id={self.id}, name={self.name}, ip={self.ip}, active={self.is_active})>"

