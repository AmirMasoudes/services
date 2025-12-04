"""
Ticket model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class TicketStatus(str, enum.Enum):
    """Ticket status enumeration"""
    OPEN = "open"
    PENDING = "pending"
    CLOSED = "closed"


class Ticket(Base):
    """Ticket model"""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN, nullable=False, index=True)
    telegram_message_id = Column(Integer, nullable=True)  # Telegram message ID for tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="tickets")
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, user_id={self.user_id}, status={self.status})>"

