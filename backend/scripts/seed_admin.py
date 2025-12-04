"""
Seed script to create first admin user
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import AsyncSessionLocal
from app.crud.user import user_crud
from app.models.user import UserRole
from app.core.security import get_password_hash


async def create_admin():
    """Create admin user"""
    async with AsyncSessionLocal() as db:
        # Check if admin already exists
        admin = await user_crud.get_by_username(db, "admin")
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_data = {
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": get_password_hash("admin123"),
            "role": UserRole.ADMIN,
            "balance": 0.00,
            "is_banned": "false",
        }
        
        admin = await user_crud.create(db, admin_data)
        print(f"Admin user created successfully!")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"Please change the password after first login!")


if __name__ == "__main__":
    asyncio.run(create_admin())

