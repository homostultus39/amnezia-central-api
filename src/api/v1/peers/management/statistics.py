from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.peer import get_peer_by_id
from src.api.v1.peers.logger import logger
from src.api.v1.peers.schemas import PeerWithStatsResponse
from src.api.v1.deps.exceptions.peer import PeerNotFoundException
from src.redis.management.cluster_status import ClusterStatusCache

router = APIRouter()
cache = ClusterStatusCache()


@router.get("/{peer_id}/statistics", response_model=PeerWithStatsResponse)
async def get_peer_stats(
    session: SessionDep,
    peer_id: UUID,
) -> PeerWithStatsResponse:
    try:
        peer = await get_peer_by_id(session, peer_id)
        if not peer:
            raise PeerNotFoundException()

        response = PeerWithStatsResponse.model_validate(peer)

        peer_status = await cache.get_peer_status(str(peer.cluster_id), peer.public_key)
        if peer_status:
            response.last_handshake = peer_status.get("last_handshake")
            response.rx_bytes = peer_status.get("rx_bytes")
            response.tx_bytes = peer_status.get("tx_bytes")
            response.online = peer_status.get("online")
            response.persistent_keepalive = peer_status.get("persistent_keepalive")
            logger.debug(f"Enriched peer stats from cache: {peer.public_key}")
        else:
            logger.warning(f"No cached stats found for peer: {peer.public_key} in cluster: {peer.cluster_id}")

        logger.info(f"Retrieved stats for peer: {peer.public_key}")
        return response

    except PeerNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting peer stats {peer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get peer stats",
        )
