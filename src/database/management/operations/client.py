import uuid
import pytz
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import ClientModel, SubscriptionStatus
from src.database.management.operations.tariff import get_tariff_by_code
from src.management.settings import get_settings

settings = get_settings()


async def get_client_by_id(session: AsyncSession, client_id: uuid.UUID) -> ClientModel | None:
    result = await session.execute(
        select(ClientModel).options(selectinload(ClientModel.peers)).where(ClientModel.id == client_id)
    )
    return result.scalar_one_or_none()


async def get_client_by_username(session: AsyncSession, username: str):
    result = await session.execute(
        select(ClientModel).where(ClientModel.username == username)
    )
    return result.scalar_one_or_none()


async def get_all_clients(session: AsyncSession):
    result = await session.execute(select(ClientModel).options(selectinload(ClientModel.peers)))
    return result.scalars().all()


async def create_client(
    session: AsyncSession,
    username: str,
    is_admin: bool = False
) -> ClientModel:
    tz = pytz.timezone(settings.timezone)
    now = datetime.now(tz)

    if is_admin:
        expires_at = None
        subscription_status = SubscriptionStatus.ACTIVE.value
        trial_used = False
    elif not settings.subscription_enabled:
        expires_at = None
        subscription_status = SubscriptionStatus.ACTIVE.value
        trial_used = False
    elif settings.trial_enabled:
        expires_at = now + timedelta(days=settings.trial_period_days)
        subscription_status = SubscriptionStatus.TRIAL.value
        trial_used = False
    else:
        expires_at = now
        subscription_status = SubscriptionStatus.EXPIRED.value
        trial_used = True

    client = ClientModel(
        username=username,
        expires_at=expires_at,
        subscription_status=subscription_status,
        trial_used=trial_used,
        last_subscription_at=None,
        is_admin=is_admin
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


async def update_client_subscription_status(
    session: AsyncSession,
    client_id: uuid.UUID,
    status: SubscriptionStatus
) -> ClientModel | None:
    client = await get_client_by_id(session, client_id)
    if not client:
        return None

    client.subscription_status = status.value
    await session.commit()
    await session.refresh(client)
    return client


async def subscribe_client(
    session: AsyncSession,
    client_id: uuid.UUID,
    tariff_code: str
) -> ClientModel:
    if not settings.subscription_enabled:
        raise ValueError("Subscriptions are disabled")

    client = await get_client_by_id(session, client_id)
    if not client:
        raise ValueError(f"Client with id {client_id} not found")

    tariff = await get_tariff_by_code(session, tariff_code)
    if not tariff or not tariff.is_active:
        raise ValueError(f"Tariff {tariff_code} is not available")

    tz = pytz.timezone(settings.timezone)
    now = datetime.now(tz)
    days = tariff.days

    if client.subscription_status == SubscriptionStatus.ACTIVE.value and client.expires_at > now:
        new_expires_at = client.expires_at + timedelta(days=days)
    else:
        new_expires_at = now + timedelta(days=days)
        if client.subscription_status == SubscriptionStatus.TRIAL.value:
            client.trial_used = True

    client.subscription_status = SubscriptionStatus.ACTIVE.value
    client.expires_at = new_expires_at
    client.last_subscription_at = now

    await session.commit()
    await session.refresh(client)
    return client


async def expire_client_subscription(
    session: AsyncSession,
    client_id: uuid.UUID
) -> ClientModel | None:
    client = await get_client_by_id(session, client_id)
    if not client:
        return None

    client.subscription_status = SubscriptionStatus.EXPIRED.value
    if client.subscription_status == SubscriptionStatus.TRIAL.value:
        client.trial_used = True

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
