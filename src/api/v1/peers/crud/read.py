from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.peer import get_peer_by_id, get_all_peers
from src.api.v1.peers.logger import logger
from src.api.v1.peers.schemas import PeerResponse
from src.api.v1.deps.exceptions.peer import PeerNotFoundException

router = APIRouter()


@router.get("/", response_model=list[PeerResponse])
async def list_peers(session: SessionDep) -> list[PeerResponse]:
    try:
        peers = await get_all_peers(session)
        result = [PeerResponse.model_validate(peer) for peer in peers]

        logger.info(f"Retrieved {len(result)} peers")
        return result

    except Exception as e:
        logger.error(f"Error listing peers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list peers",
        )


@router.get("/{peer_id}", response_model=PeerResponse)
async def get_peer(
    session: SessionDep,
    peer_id: UUID,
) -> PeerResponse:
    try:
        peer = await get_peer_by_id(session, peer_id)
        if not peer:
            raise PeerNotFoundException()

        logger.info(f"Retrieved peer: {peer.public_key}")
        return PeerResponse.model_validate(peer)

    except PeerNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting peer {peer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get peer",
        )
