"""
Finance/Expense model
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Expense(Base):
    """Expense model for tracking costs"""
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=True)  # e.g., "server", "domain", "marketing"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_by = Column(Integer, nullable=True)  # Admin user ID who created this expense
    
    def __repr__(self):
        return f"<Expense(id={self.id}, description={self.description}, amount={self.amount})>"

