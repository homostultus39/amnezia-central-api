from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.cluster import get_cluster_by_name, create_cluster
from src.api.v1.clusters.logger import logger
from src.api.v1.clusters.schemas import CreateClusterRequest, ClusterResponse

router = APIRouter()


@router.post("/", response_model=ClusterResponse)
async def create_cluster_endpoint(
    session: SessionDep,
    payload: CreateClusterRequest,
) -> ClusterResponse:
    try:
        existing_cluster = await get_cluster_by_name(session, payload.name)
        if existing_cluster:
            logger.warning(f"Attempted to create cluster with existing name: {payload.name}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cluster with this name already exists",
            )

        cluster = await create_cluster(
            session,
            name=payload.name,
            endpoint=payload.endpoint,
            api_key=payload.api_key,
        )

        logger.info(f"Cluster created: {cluster.name} ({cluster.id})")
        return ClusterResponse.model_validate(cluster)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating cluster: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create cluster",
        )
