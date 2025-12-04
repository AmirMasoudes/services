"""
Order CRUD operations
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta, date as date_type
from app.models.order import Order, OrderStatus
from app.crud.base import CRUDBase


class CRUDOrder(CRUDBase[Order]):
    """Order CRUD operations"""
    
    async def get_by_user(self, db: AsyncSession, user_id: int) -> List[Order]:
        """Get all orders for a user"""
        result = await db.execute(
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_status(self, db: AsyncSession, status: OrderStatus) -> List[Order]:
        """Get orders by status"""
        result = await db.execute(
            select(self.model)
            .where(self.model.status == status)
            .order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_stats(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get order statistics"""
        query = select(
            func.count(self.model.id).label("total_orders"),
            func.sum(self.model.amount).label("total_income"),
            func.sum(self.model.profit).label("total_profit"),
            func.sum(
                func.case((self.model.status == OrderStatus.PENDING, 1), else_=0)
            ).label("pending_orders"),
            func.sum(
                func.case((self.model.status == OrderStatus.COMPLETED, 1), else_=0)
            ).label("completed_orders"),
            func.sum(
                func.case((self.model.status == OrderStatus.CANCELLED, 1), else_=0)
            ).label("cancelled_orders"),
        )
        
        if start_date:
            query = query.where(self.model.created_at >= start_date)
        if end_date:
            query = query.where(self.model.created_at <= end_date)
        
        result = await db.execute(query)
        row = result.first()
        
        return {
            "total_orders": row.total_orders or 0,
            "total_income": float(row.total_income or 0),
            "total_profit": float(row.total_profit or 0),
            "pending_orders": row.pending_orders or 0,
            "completed_orders": row.completed_orders or 0,
            "cancelled_orders": row.cancelled_orders or 0,
        }
    
    async def get_income_by_period(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Get total income for a period"""
        result = await db.execute(
            select(func.sum(self.model.amount))
            .where(
                and_(
                    self.model.status == OrderStatus.COMPLETED,
                    self.model.created_at >= start_date,
                    self.model.created_at <= end_date
                )
            )
        )
        total = result.scalar() or 0
        return float(total)
    
    async def get_with_relations(
        self,
        db: AsyncSession,
        order_id: int
    ) -> Optional[Order]:
        """Get order with user relation"""
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.user))
            .where(self.model.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
        start_date: Optional[date_type] = None,
        end_date: Optional[date_type] = None,
        order_by: Optional[str] = None
    ) -> Tuple[List[Order], int]:
        """Get multiple orders with date filtering"""
        from sqlalchemy.orm import selectinload
        
        query = select(self.model).options(selectinload(self.model.user))
        count_query = select(func.count()).select_from(self.model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)
                    count_query = count_query.where(getattr(self.model, key) == value)
        
        # Apply date filters
        if start_date:
            start_dt = datetime.combine(start_date, datetime.min.time())
            query = query.where(self.model.created_at >= start_dt)
            count_query = count_query.where(self.model.created_at >= start_dt)
        if end_date:
            end_dt = datetime.combine(end_date, datetime.max.time())
            query = query.where(self.model.created_at <= end_dt)
            count_query = count_query.where(self.model.created_at <= end_dt)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply ordering
        if order_by:
            if order_by.startswith("-"):
                order_field = getattr(self.model, order_by[1:], None)
                if order_field:
                    query = query.order_by(order_field.desc())
            else:
                order_field = getattr(self.model, order_by, None)
                if order_field:
                    query = query.order_by(order_field)
        else:
            query = query.order_by(self.model.id.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_summary_stats(
        self,
        db: AsyncSession,
        start_date: Optional[date_type] = None,
        end_date: Optional[date_type] = None
    ) -> dict:
        """Get summary statistics for orders"""
        from app.models.order import OrderStatus
        
        start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
        end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None
        
        stats = await self.get_stats(db, start_dt, end_dt)
        
        # Add daily breakdown if date range provided
        daily_breakdown = []
        if start_date and end_date:
            current = start_date
            while current <= end_date:
                day_start = datetime.combine(current, datetime.min.time())
                day_end = datetime.combine(current, datetime.max.time())
                day_income = await self.get_income_by_period(db, day_start, day_end)
                daily_breakdown.append({
                    "date": current.isoformat(),
                    "income": day_income
                })
                current += timedelta(days=1)
        
        stats["daily_breakdown"] = daily_breakdown
        return stats


order_crud = CRUDOrder(Order)

