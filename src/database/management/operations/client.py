from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import ClientModel


async def get_client_by_id(session: AsyncSession, client_id):
    """Get client by ID."""
    result = await session.execute(
        select(ClientModel).where(ClientModel.id == client_id)
    )
    return result.scalar_one_or_none()


async def get_client_by_username(session: AsyncSession, username: str):
    """Get client by username."""
    result = await session.execute(
        select(ClientModel).where(ClientModel.username == username)
    )
    return result.scalar_one_or_none()


async def get_all_clients(session: AsyncSession):
    """Get all clients."""
    result = await session.execute(select(ClientModel))
    return result.scalars().all()
