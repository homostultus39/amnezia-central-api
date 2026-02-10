from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import AdminModel
from src.management.security import hash_password


async def get_admin_by_username(session: AsyncSession, username: str):
    """Get admin by username."""
    result = await session.execute(
        select(AdminModel).where(AdminModel.username == username)
    )
    return result.scalar_one_or_none()


async def create_admin(session: AsyncSession, username: str, password: str) -> AdminModel:
    """Create admin user with hashed password."""
    admin = AdminModel(
        username=username,
        pwd_hash=hash_password(password)
    )
    session.add(admin)
    await session.commit()
    return admin
