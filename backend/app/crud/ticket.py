"""
Ticket CRUD operations
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ticket import Ticket, TicketStatus
from app.crud.base import CRUDBase


class CRUDTicket(CRUDBase[Ticket]):
    """Ticket CRUD operations"""
    
    async def get_by_user(self, db: AsyncSession, user_id: int) -> List[Ticket]:
        """Get all tickets for a user"""
        result = await db.execute(
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_status(self, db: AsyncSession, status: TicketStatus) -> List[Ticket]:
        """Get tickets by status"""
        result = await db.execute(
            select(self.model)
            .where(self.model.status == status)
            .order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_open_tickets(self, db: AsyncSession) -> List[Ticket]:
        """Get all open tickets"""
        return await self.get_by_status(db, TicketStatus.OPEN)
    
    async def get_by_telegram_message_id(
        self,
        db: AsyncSession,
        telegram_message_id: int
    ) -> Optional[Ticket]:
        """Get ticket by Telegram message ID"""
        result = await db.execute(
            select(self.model).where(
                self.model.telegram_message_id == telegram_message_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_with_relations(
        self,
        db: AsyncSession,
        ticket_id: int
    ) -> Optional[Ticket]:
        """Get ticket with user relation"""
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.user))
            .where(self.model.id == ticket_id)
        )
        return result.scalar_one_or_none()


ticket_crud = CRUDTicket(Ticket)

