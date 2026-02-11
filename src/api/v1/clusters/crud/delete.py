from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.cluster import get_cluster_by_id, delete_cluster
from src.api.v1.clusters.logger import logger
from src.api.v1.deps.exceptions.cluster import ClusterNotFoundException
from src.redis.management.cluster_status import ClusterStatusCache

router = APIRouter()
cache = ClusterStatusCache()


@router.delete("/{cluster_id}")
async def delete_cluster_endpoint(
    session: SessionDep,
    cluster_id: UUID,
) -> dict:
    try:
        cluster = await get_cluster_by_id(session, cluster_id)
        if not cluster:
            raise ClusterNotFoundException()

        success = await delete_cluster(session, cluster_id)
        if not success:
            raise ClusterNotFoundException()

        await cache.clear_cluster_cache(str(cluster_id))

        logger.info(f"Cluster deleted: {cluster.name} ({cluster_id})")
        return {"message": "Cluster deleted successfully"}

    except ClusterNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete cluster",
        )
