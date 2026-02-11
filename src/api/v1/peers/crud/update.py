from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.peer import get_peer_by_id, update_peer
from src.api.v1.peers.logger import logger
from src.api.v1.peers.schemas import UpdatePeerRequest, PeerResponse, ClusterPeerResponse
from src.api.v1.deps.exceptions.peer import PeerNotFoundException
from src.api.v1.clusters.management.http_client import ClusterAPIClient
from src.management.security import hash_password
from src.database.models import AppType

router = APIRouter()


@router.patch("/{peer_id}", response_model=PeerResponse)
async def update_peer_endpoint(
    session: SessionDep,
    peer_id: UUID,
    payload: UpdatePeerRequest,
) -> PeerResponse:
    try:
        peer = await get_peer_by_id(session, peer_id)
        if not peer:
            raise PeerNotFoundException()

        new_app_type = payload.app_type if payload.app_type else peer.app_type
        new_protocol = payload.protocol if payload.protocol else peer.protocol

        if new_app_type == peer.app_type and new_protocol == peer.protocol:
            logger.info(f"No changes for peer {peer_id}, returning current state")
            return PeerResponse.model_validate(peer)

        try:
            cluster_client = ClusterAPIClient(peer.cluster.endpoint, peer.cluster.api_key)
            await cluster_client.delete_peer(peer_id)
            logger.info(f"Old peer deleted from cluster: {peer.cluster.name}")
        except Exception as e:
            logger.error(f"Failed to delete old peer from cluster: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to delete peer from cluster",
            )

        try:
            cluster_response = await cluster_client.create_peer(
                app_type=new_app_type,
                protocol=new_protocol,
            )
            peer_data = ClusterPeerResponse.model_validate(cluster_response)
            logger.info(f"New peer generated on cluster: {peer.cluster.name}")
        except Exception as e:
            logger.error(f"Failed to create new peer on cluster: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to create peer on cluster",
            )

        private_key_hash = hash_password(peer_data.private_key)

        updated_peer = await update_peer(
            session,
            peer_id,
            public_key=peer_data.public_key,
            private_key_hash=private_key_hash,
            allocated_ip=peer_data.allocated_ip,
            endpoint=peer_data.endpoint,
            app_type=AppType(new_app_type),
            protocol=new_protocol,
        )

        logger.info(f"Peer updated: {updated_peer.public_key} ({peer_id})")
        return PeerResponse.model_validate(updated_peer)

    except PeerNotFoundException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating peer {peer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update peer",
        )
