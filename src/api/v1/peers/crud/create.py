from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.peer import get_peer_by_public_key, create_peer
from src.database.management.operations.client import get_client_by_id
from src.database.management.operations.cluster import get_cluster_by_id
from src.api.v1.peers.logger import logger
from src.api.v1.peers.schemas import CreatePeerRequest, PeerResponse, ClusterPeerResponse
from src.api.v1.management.exceptions.peer import PeerAlreadyExistsException
from src.api.v1.management.exceptions.client import ClientNotFoundException
from src.api.v1.management.exceptions.cluster import ClusterNotFoundException
from src.api.v1.management.http_client import ClusterAPIClient
from src.management.security import hash_password
from src.minio import MinioClient

router = APIRouter()
minio_client = MinioClient()


@router.post("/", response_model=PeerResponse)
async def create_peer_endpoint(
    session: SessionDep,
    payload: CreatePeerRequest,
) -> PeerResponse:
    try:
        client = await get_client_by_id(session, payload.client_id)
        if not client:
            raise ClientNotFoundException()

        cluster = await get_cluster_by_id(session, payload.cluster_id)
        if not cluster:
            raise ClusterNotFoundException()

        try:
            cluster_client = ClusterAPIClient(cluster.endpoint, cluster.api_key)
            cluster_response = await cluster_client.create_peer(
                app_type=payload.app_type.value,
                protocol=payload.protocol,
            )
            peer_data = ClusterPeerResponse.model_validate(cluster_response)
            logger.info(f"Peer generated on cluster: {cluster.name}")
        except Exception as e:
            logger.error(f"Failed to create peer on cluster {cluster.name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to create peer on cluster",
            )

        existing_peer = await get_peer_by_public_key(session, peer_data.public_key)
        if existing_peer:
            logger.warning(f"Peer with public key already exists: {peer_data.public_key}")
            raise PeerAlreadyExistsException()

        private_key_hash = hash_password(peer_data.private_key)

        peer = await create_peer(
            session,
            client_id=payload.client_id,
            cluster_id=payload.cluster_id,
            public_key=peer_data.public_key,
            private_key_hash=private_key_hash,
            allocated_ip=peer_data.allocated_ip,
            endpoint=peer_data.endpoint,
            app_type=payload.app_type.value,
            protocol=payload.protocol,
        )
        config_download_url = await minio_client.save_peer_config(peer.id, peer_data.config)

        logger.info(f"Peer created: {peer.public_key} ({peer.id})")
        response = PeerResponse.model_validate(peer)
        response.config = peer_data.config
        response.config_download_url = config_download_url
        return response

    except (ClientNotFoundException, ClusterNotFoundException, PeerAlreadyExistsException):
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating peer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create peer",
        )
