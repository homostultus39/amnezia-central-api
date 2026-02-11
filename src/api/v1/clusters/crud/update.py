from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.cluster import get_cluster_by_id, update_cluster
from src.api.v1.clusters.logger import logger
from src.api.v1.clusters.schemas import UpdateClusterRequest, ClusterResponse
from src.api.v1.deps.exceptions.cluster import ClusterNotFoundException

router = APIRouter()


@router.patch("/{cluster_id}", response_model=ClusterResponse)
async def update_cluster_endpoint(
    session: SessionDep,
    cluster_id: UUID,
    payload: UpdateClusterRequest,
) -> ClusterResponse:
    try:
        cluster = await get_cluster_by_id(session, cluster_id)
        if not cluster:
            raise ClusterNotFoundException()

        updated_cluster = await update_cluster(
            session,
            cluster_id,
            name=payload.name,
            endpoint=payload.endpoint,
            api_key=payload.api_key,
            is_active=payload.is_active,
        )

        logger.info(f"Cluster updated: {updated_cluster.name} ({cluster_id})")
        return ClusterResponse.model_validate(updated_cluster)

    except ClusterNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error updating cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cluster",
        )
