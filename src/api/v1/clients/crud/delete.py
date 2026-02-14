from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.client import get_client_by_id, delete_client
from src.database.management.operations.peer import get_peers_by_client_id
from src.database.management.operations.cluster import get_cluster_by_id
from src.api.v1.clients.logger import logger
from src.api.v1.management.exceptions.client import ClientNotFoundException
from src.api.v1.management.http_client import ClusterAPIClient

router = APIRouter()


@router.delete("/{client_id}")
async def delete_client_endpoint(
    session: SessionDep,
    client_id: UUID,
) -> dict:
    try:
        client = await get_client_by_id(session, client_id)
        if not client:
            raise ClientNotFoundException()

        peers = await get_peers_by_client_id(session, client_id)

        for peer in peers:
            try:
                cluster = await get_cluster_by_id(session, peer.cluster_id)
                if not cluster:
                    logger.error(f"Cluster not found for peer {peer.id}: {peer.cluster_id}")
                    continue
                cluster_client = ClusterAPIClient(cluster.endpoint, cluster.api_key)
                await cluster_client.delete_peer(peer.public_key)
                logger.info(f"Peer deleted from cluster: {peer.public_key} on {cluster.name}")
            except Exception as e:
                logger.error(f"Failed to delete peer {peer.id} from cluster: {e}")

        success = await delete_client(session, client_id)
        if not success:
            raise ClientNotFoundException()

        logger.info(f"Client deleted: {client.username} ({client_id})")
        return {"message": "Client deleted successfully"}

    except ClientNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete client",
        )
