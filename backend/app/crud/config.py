"""
Config CRUD operations
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timezone
from app.models.config import Config, ConfigStatus
from app.crud.base import CRUDBase


class CRUDConfig(CRUDBase[Config]):
    """Config CRUD operations"""
    
    async def get_by_user(self, db: AsyncSession, user_id: int) -> List[Config]:
        """Get all configs for a user"""
        result = await db.execute(
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_server(self, db: AsyncSession, server_id: int) -> List[Config]:
        """Get all configs for a server"""
        result = await db.execute(
            select(self.model)
            .where(self.model.server_id == server_id)
        )
        return list(result.scalars().all())
    
    async def get_by_sui_client_id(
        self,
        db: AsyncSession,
        sui_client_id: str
    ) -> Optional[Config]:
        """Get config by S-UI client ID"""
        result = await db.execute(
            select(self.model).where(self.model.sui_client_id == sui_client_id)
        )
        return result.scalar_one_or_none()
    
    async def get_expired_configs(self, db: AsyncSession) -> List[Config]:
        """Get all expired configs"""
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(self.model)
            .where(
                and_(
                    self.model.expire_at.isnot(None),
                    self.model.expire_at < now,
                    self.model.status == ConfigStatus.ACTIVE
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_over_limit_configs(self, db: AsyncSession) -> List[Config]:
        """Get configs that exceeded data limit"""
        result = await db.execute(
            select(self.model)
            .where(
                and_(
                    self.model.data_limit_gb.isnot(None),
                    self.model.used_data_gb >= self.model.data_limit_gb,
                    self.model.status == ConfigStatus.ACTIVE
                )
            )
        )
        return list(result.scalars().all())
    
    async def update_usage(
        self,
        db: AsyncSession,
        config_id: int,
        used_data_gb: float
    ) -> Optional[Config]:
        """Update config usage"""
        config = await self.get(db, config_id)
        if not config:
            return None
        
        from decimal import Decimal
        config.used_data_gb = Decimal(str(used_data_gb))
        await db.commit()
        await db.refresh(config)
        return config
    
    async def get_with_relations(
        self,
        db: AsyncSession,
        config_id: int
    ) -> Optional[Config]:
        """Get config with user and server relations"""
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(self.model)
            .options(
                selectinload(self.model.user),
                selectinload(self.model.server)
            )
            .where(self.model.id == config_id)
        )
        return result.scalar_one_or_none()


config_crud = CRUDConfig(Config)

