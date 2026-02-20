import uuid
from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import ClusterModel, ClientModel, PeerModel


async def get_clusters_counts(session: AsyncSession) -> dict:
    result = await session.execute(
        select(ClusterModel.is_active, func.count().label("count"))
        .group_by(ClusterModel.is_active)
    )
    rows = result.all()
    active = 0
    inactive = 0
    for is_active, count in rows:
        if is_active:
            active = count
        else:
            inactive = count
    return {"total": active + inactive, "active": active, "inactive": inactive}


async def get_clients_counts(session: AsyncSession) -> dict:
    result = await session.execute(
        select(ClientModel.subscription_status, func.count().label("count"))
        .group_by(ClientModel.subscription_status)
    )
    rows = result.all()
    by_status = {}
    for status, count in rows:
        by_status[status] = count
    total = sum(by_status.values())
    return {"total": total, "by_status": by_status}


async def get_peers_counts(session: AsyncSession) -> dict:
    result = await session.execute(
        select(PeerModel.app_type, func.count().label("count"))
        .group_by(PeerModel.app_type)
    )
    rows = result.all()
    by_app_type = {}
    for app_type, count in rows:
        by_app_type[app_type] = count
    total = sum(by_app_type.values())
    return {"total": total, "by_app_type": by_app_type}


async def get_cluster_peers_counts(
    session: AsyncSession,
    cluster_id: uuid.UUID,
) -> dict:
    result = await session.execute(
        select(PeerModel.app_type, func.count().label("count"))
        .where(PeerModel.cluster_id == cluster_id)
        .group_by(PeerModel.app_type)
    )
    rows = result.all()
    by_app_type = {}
    for app_type, count in rows:
        by_app_type[app_type] = count
    total = sum(by_app_type.values())
    return {"total": total, "by_app_type": by_app_type}


async def get_cluster_unique_clients_count(
    session: AsyncSession,
    cluster_id: uuid.UUID,
) -> int:
    result = await session.execute(
        select(func.count(distinct(PeerModel.client_id)))
        .where(PeerModel.cluster_id == cluster_id)
    )
    return result.scalar_one()
