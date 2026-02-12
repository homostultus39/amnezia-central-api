from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.peer import get_peer_by_id, delete_peer
from src.database.management.operations.cluster import get_cluster_by_id
from src.api.v1.peers.logger import logger
from src.api.v1.deps.exceptions.peer import PeerNotFoundException
from src.api.v1.management.http_client import ClusterAPIClient
from src.minio import MinioClient

router = APIRouter()
minio_client = MinioClient()


@router.delete("/{peer_id}")
async def delete_peer_endpoint(
    session: SessionDep,
    peer_id: UUID,
) -> dict:
    try:
        peer = await get_peer_by_id(session, peer_id)
        if not peer:
            raise PeerNotFoundException()

        cluster = await get_cluster_by_id(session, peer.cluster_id)
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Peer cluster is not available",
            )

        try:
            cluster_client = ClusterAPIClient(cluster.endpoint, cluster.api_key)
            await cluster_client.delete_peer(peer.public_key)
            logger.info(f"Peer deleted from cluster: {cluster.name}")
        except Exception as e:
            logger.error(f"Failed to delete peer from cluster: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to delete peer from cluster",
            )

        success = await delete_peer(session, peer_id)
        if not success:
            raise PeerNotFoundException()
        await minio_client.delete_peer_config(peer_id)

        logger.info(f"Peer deleted: {peer.public_key} ({peer_id})")
        return {"message": "Peer deleted successfully"}

    except PeerNotFoundException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting peer {peer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete peer",
        )
