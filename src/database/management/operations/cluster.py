import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from src.database.models import ClusterModel


async def get_cluster_by_id(session: AsyncSession, cluster_id: uuid.UUID) -> ClusterModel | None:
    result = await session.execute(
        select(ClusterModel).where(ClusterModel.id == cluster_id)
    )
    return result.scalar_one_or_none()


async def get_cluster_by_name(session: AsyncSession, name: str) -> ClusterModel | None:
    result = await session.execute(
        select(ClusterModel).where(ClusterModel.name == name)
    )
    return result.scalar_one_or_none()


async def get_all_clusters(session: AsyncSession) -> list[ClusterModel]:
    result = await session.execute(select(ClusterModel))
    return result.scalars().all()


async def create_cluster(session: AsyncSession, name: str, endpoint: str, api_key: str) -> ClusterModel:
    cluster = ClusterModel(
        name=name,
        endpoint=endpoint,
        api_key=api_key
    )
    session.add(cluster)
    await session.commit()
    await session.refresh(cluster)
    return cluster


async def update_cluster(
    session: AsyncSession,
    cluster_id: uuid.UUID,
    name: str | None = None,
    endpoint: str | None = None,
    api_key: str | None = None,
    is_active: bool | None = None
) -> ClusterModel | None:
    cluster = await get_cluster_by_id(session, cluster_id)
    if not cluster:
        return None

    if name is not None:
        cluster.name = name
    if endpoint is not None:
        cluster.endpoint = endpoint
    if api_key is not None:
        cluster.api_key = api_key
    if is_active is not None:
        cluster.is_active = is_active

    await session.commit()
    await session.refresh(cluster)
    return cluster


async def delete_cluster(session: AsyncSession, cluster_id: uuid.UUID) -> bool:
    cluster = await get_cluster_by_id(session, cluster_id)
    if not cluster:
        return False

    await session.delete(cluster)
    await session.commit()
    return True


async def update_last_handshake(session: AsyncSession, cluster_id: uuid.UUID) -> bool:
    cluster = await get_cluster_by_id(session, cluster_id)
    if not cluster:
        return False

    cluster.last_handshake = datetime.now(timezone.utc)
    await session.commit()
    return True
