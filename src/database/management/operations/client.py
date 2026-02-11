import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import ClientModel


async def get_client_by_id(session: AsyncSession, client_id: uuid.UUID) -> ClientModel | None:
    result = await session.execute(
        select(ClientModel).where(ClientModel.id == client_id)
    )
    return result.scalar_one_or_none()


async def get_client_by_username(session: AsyncSession, username: str):
    result = await session.execute(
        select(ClientModel).where(ClientModel.username == username)
    )
    return result.scalar_one_or_none()


async def get_all_clients(session: AsyncSession):
    result = await session.execute(select(ClientModel))
    return result.scalars().all()


async def create_client(
    session: AsyncSession,
    username: str,
    expires_at: datetime
) -> ClientModel:
    client = ClientModel(
        username=username,
        expires_at=expires_at
    )
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client


async def update_client(
    session: AsyncSession,
    client_id: uuid.UUID,
    expires_at: datetime
) -> ClientModel | None:
    client = await get_client_by_id(session, client_id)
    if not client:
        return None

    client.expires_at = expires_at
    await session.commit()
    await session.refresh(client)
    return client


async def delete_client(session: AsyncSession, client_id: uuid.UUID) -> bool:
    client = await get_client_by_id(session, client_id)
    if not client:
        return False

    await session.delete(client)
    await session.commit()
    return True
