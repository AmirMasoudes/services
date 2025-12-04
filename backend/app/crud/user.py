"""
User CRUD operations
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.crud.base import CRUDBase
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User]):
    """User CRUD operations"""
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(
            select(self.model).where(self.model.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_tg_id(self, db: AsyncSession, tg_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        result = await db.execute(
            select(self.model).where(self.model.tg_id == tg_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, obj_in: dict) -> User:
        """Create user with hashed password"""
        if "password" in obj_in:
            obj_in["password_hash"] = get_password_hash(obj_in.pop("password"))
        return await super().create(db, obj_in)
    
    async def authenticate(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = await self.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    async def update_balance(
        self,
        db: AsyncSession,
        user_id: int,
        amount: float
    ) -> Optional[User]:
        """Update user balance"""
        user = await self.get(db, user_id)
        if not user:
            return None
        
        from decimal import Decimal
        user.balance = Decimal(str(float(user.balance) + amount))
        await db.commit()
        await db.refresh(user)
        return user
    
    async def get_with_stats(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user with related statistics"""
        result = await db.execute(
            select(self.model)
            .options(
                selectinload(self.model.configs),
                selectinload(self.model.orders),
                selectinload(self.model.tickets)
            )
            .where(self.model.id == user_id)
        )
        return result.scalar_one_or_none()


user_crud = CRUDUser(User)

