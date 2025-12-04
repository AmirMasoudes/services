"""
Finance schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ExpenseBase(BaseModel):
    """Base expense schema"""
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., ge=0, description="Expense amount")
    category: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    """Expense creation schema"""
    pass


class ExpenseUpdate(BaseModel):
    """Expense update schema"""
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    """Expense response schema"""
    id: int
    created_at: datetime
    created_by: Optional[int] = None
    
    @classmethod
    def from_orm(cls, obj):
        """Create from ORM object"""
        return cls(
            id=obj.id,
            description=obj.description,
            amount=float(obj.amount),
            category=obj.category,
            notes=obj.notes,
            created_at=obj.created_at,
            created_by=obj.created_by
        )
    
    class Config:
        from_attributes = True


class FinanceStatsResponse(BaseModel):
    """Finance statistics response"""
    total_income: float
    total_expenses: float
    net_profit: float
    period_start: datetime
    period_end: datetime


class FinanceSummary(BaseModel):
    """Finance summary response"""
    total_income: float
    total_expenses: float
    net_profit: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class FinanceStats(BaseModel):
    """Finance statistics for charts"""
    period: str
    labels: list[str]
    income: list[float]
    expenses: list[float]
    net_profit: list[float]


class FinanceDashboardResponse(BaseModel):
    """Finance dashboard response"""
    today_income: float
    today_expenses: float
    today_profit: float
    week_income: float
    week_expenses: float
    week_profit: float
    month_income: float
    month_expenses: float
    month_profit: float
    total_income: float
    total_expenses: float
    total_profit: float

