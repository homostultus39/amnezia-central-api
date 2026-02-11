from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.cluster import (
    get_cluster_by_id,
    get_all_clusters,
    update_last_handshake,
)
from src.api.v1.clusters.logger import logger
from src.api.v1.clusters.crud.management.cluster_status import enrich_cluster_status
from src.api.v1.clusters.schemas import ClusterWithStatusResponse
from src.api.v1.deps.exceptions.cluster import ClusterNotFoundException

router = APIRouter()


@router.get("/", response_model=list[ClusterWithStatusResponse])
async def list_clusters(session: SessionDep) -> list[ClusterWithStatusResponse]:
    try:
        clusters = await get_all_clusters(session)
        result = []

        for cluster in clusters:
            response = ClusterWithStatusResponse.model_validate(cluster)
            await enrich_cluster_status(response, cluster.id)
            result.append(response)

        logger.info(f"Retrieved {len(result)} clusters")
        return result

    except Exception as e:
        logger.error(f"Error listing clusters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list clusters",
        )


@router.get("/{cluster_id}", response_model=ClusterWithStatusResponse)
async def get_cluster(
    session: SessionDep,
    cluster_id: UUID,
) -> ClusterWithStatusResponse:
    try:
        cluster = await get_cluster_by_id(session, cluster_id)
        if not cluster:
            raise ClusterNotFoundException()

        response = ClusterWithStatusResponse.model_validate(cluster)
        await update_last_handshake(session, cluster_id)
        await enrich_cluster_status(response, cluster_id)

        logger.info(f"Retrieved cluster: {cluster.name}")
        return response

    except ClusterNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cluster",
        )
