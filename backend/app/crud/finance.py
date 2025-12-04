"""
Finance/Expense CRUD operations
"""
from typing import Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, date, timedelta
from app.models.finance import Expense
from app.models.order import Order, OrderStatus
from app.crud.base import CRUDBase
from app.crud.order import order_crud


class CRUDFinance:
    """Finance CRUD operations"""
    
    def __init__(self):
        self.expense_crud = CRUDBase(Expense)
    
    async def create_expense(
        self,
        db: AsyncSession,
        expense_data: dict
    ) -> Expense:
        """Create expense"""
        return await self.expense_crud.create(db, expense_data)
    
    async def get_expense(
        self,
        db: AsyncSession,
        expense_id: int
    ) -> Optional[Expense]:
        """Get expense by ID"""
        return await self.expense_crud.get(db, expense_id)
    
    async def update_expense(
        self,
        db: AsyncSession,
        expense: Expense,
        expense_data: dict
    ) -> Expense:
        """Update expense"""
        return await self.expense_crud.update(db, expense, expense_data)
    
    async def delete_expense(
        self,
        db: AsyncSession,
        expense_id: int
    ) -> bool:
        """Delete expense"""
        return await self.expense_crud.delete(db, expense_id)
    
    async def get_expenses(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Tuple[List[Expense], int]:
        """Get expenses with pagination and date filtering"""
        query = select(Expense)
        count_query = select(func.count()).select_from(Expense)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(Expense, key) and value is not None:
                    query = query.where(getattr(Expense, key) == value)
                    count_query = count_query.where(getattr(Expense, key) == value)
        
        # Apply date filters
        if start_date:
            start_dt = datetime.combine(start_date, datetime.min.time())
            query = query.where(Expense.created_at >= start_dt)
            count_query = count_query.where(Expense.created_at >= start_dt)
        if end_date:
            end_dt = datetime.combine(end_date, datetime.max.time())
            query = query.where(Expense.created_at <= end_dt)
            count_query = count_query.where(Expense.created_at <= end_dt)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply ordering and pagination
        query = query.order_by(Expense.id.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_total_expenses(
        self,
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> float:
        """Get total expenses for a period"""
        query = select(func.sum(Expense.amount))
        
        if start_date:
            start_dt = datetime.combine(start_date, datetime.min.time())
            query = query.where(Expense.created_at >= start_dt)
        if end_date:
            end_dt = datetime.combine(end_date, datetime.max.time())
            query = query.where(Expense.created_at <= end_dt)
        
        result = await db.execute(query)
        total = result.scalar() or 0
        return float(total)
    
    async def get_summary(
        self,
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """Get finance summary"""
        # Get total income from completed orders
        start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
        end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None
        
        total_income = await order_crud.get_income_by_period(
            db,
            start_dt or datetime.min,
            end_dt or datetime.now()
        )
        
        # Get total expenses
        total_expenses = await self.get_total_expenses(db, start_date, end_date)
        
        # Calculate net profit
        net_profit = total_income - total_expenses
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        }
    
    async def get_stats(
        self,
        db: AsyncSession,
        period: str = "month"
    ) -> dict:
        """Get finance statistics for charts"""
        now = datetime.now()
        
        if period == "day":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
            intervals = 24
            delta = timedelta(hours=1)
        elif period == "week":
            start = now - timedelta(days=7)
            end = now
            intervals = 7
            delta = timedelta(days=1)
        elif period == "month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
            intervals = 30
            delta = timedelta(days=1)
        else:  # year
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
            intervals = 12
            delta = timedelta(days=30)
        
        income_data = []
        expense_data = []
        labels = []
        
        current = start
        for i in range(intervals):
            period_start = current
            period_end = min(current + delta, end)
            
            # Get income for this period
            period_income = await order_crud.get_income_by_period(db, period_start, period_end)
            
            # Get expenses for this period
            period_expenses = await self.get_total_expenses(
                db,
                period_start.date(),
                period_end.date()
            )
            
            income_data.append(period_income)
            expense_data.append(period_expenses)
            
            if period == "day":
                labels.append(period_start.strftime("%H:00"))
            elif period == "week":
                labels.append(period_start.strftime("%Y-%m-%d"))
            elif period == "month":
                labels.append(period_start.strftime("%Y-%m-%d"))
            else:
                labels.append(period_start.strftime("%Y-%m"))
            
            current = period_end
        
        return {
            "period": period,
            "labels": labels,
            "income": income_data,
            "expenses": expense_data,
            "net_profit": [i - e for i, e in zip(income_data, expense_data)]
        }


finance_crud = CRUDFinance()

