from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import ClusterModel


async def get_cluster_by_id(session: AsyncSession, cluster_id):
    """Get cluster by ID."""
    result = await session.execute(
        select(ClusterModel).where(ClusterModel.id == cluster_id)
    )
    return result.scalar_one_or_none()


async def get_cluster_by_name(session: AsyncSession, name: str):
    """Get cluster by name."""
    result = await session.execute(
        select(ClusterModel).where(ClusterModel.name == name)
    )
    return result.scalar_one_or_none()


async def get_all_clusters(session: AsyncSession):
    """Get all clusters."""
    result = await session.execute(select(ClusterModel))
    return result.scalars().all()
