"""
Server CRUD operations
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.server import Server
from app.crud.base import CRUDBase


class CRUDServer(CRUDBase[Server]):
    """Server CRUD operations"""
    
    async def get_by_ip(self, db: AsyncSession, ip: str) -> Optional[Server]:
        """Get server by IP address"""
        result = await db.execute(
            select(self.model).where(self.model.ip == ip)
        )
        return result.scalar_one_or_none()
    
    async def get_active_servers(self, db: AsyncSession) -> List[Server]:
        """Get all active servers"""
        result = await db.execute(
            select(self.model)
            .where(self.model.is_active == True)
            .order_by(self.model.current_config_count.asc())
        )
        return list(result.scalars().all())
    
    async def find_available_server(self, db: AsyncSession) -> Optional[Server]:
        """Get server with available capacity"""
        result = await db.execute(
            select(self.model)
            .where(
                and_(
                    self.model.is_active == True,
                    self.model.current_config_count < self.model.max_config_limit
                )
            )
            .order_by(self.model.current_config_count.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_available_server(self, db: AsyncSession) -> Optional[Server]:
        """Alias for find_available_server"""
        return await self.find_available_server(db)
    
    async def increment_config_count(self, db: AsyncSession, server_id: int) -> Optional[Server]:
        """Increment server config count"""
        server = await self.get(db, server_id)
        if not server:
            return None
        
        server.current_config_count += 1
        await db.commit()
        await db.refresh(server)
        return server
    
    async def decrement_config_count(self, db: AsyncSession, server_id: int) -> Optional[Server]:
        """Decrement server config count"""
        server = await self.get(db, server_id)
        if not server:
            return None
        
        if server.current_config_count > 0:
            server.current_config_count -= 1
            await db.commit()
            await db.refresh(server)
        return server


server_crud = CRUDServer(Server)

