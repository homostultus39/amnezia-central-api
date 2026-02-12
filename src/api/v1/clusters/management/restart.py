from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.cluster import get_cluster_by_id
from src.api.v1.clusters.logger import logger
from src.api.v1.clusters.schemas import RestartClusterResponse
from src.api.v1.deps.exceptions.cluster import ClusterNotFoundException, ClusterAPIException
from src.api.v1.management.http_client import ClusterAPIClient

router = APIRouter()


@router.post("/{cluster_id}/restart", response_model=RestartClusterResponse)
async def restart_cluster(
    session: SessionDep,
    cluster_id: UUID,
) -> RestartClusterResponse:
    try:
        cluster = await get_cluster_by_id(session, cluster_id)
        if not cluster:
            raise ClusterNotFoundException()

        logger.info(f"Initiating restart for cluster: {cluster.name}")

        client = ClusterAPIClient(cluster.endpoint, cluster.api_key)
        await client.restart_server()

        logger.info(f"Cluster restarted: {cluster.name}")
        return RestartClusterResponse(
            cluster_id=cluster_id,
            status="restarted",
            message="Cluster restart initiated",
        )

    except ClusterNotFoundException:
        raise
    except ClusterAPIException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restart cluster",
        )
