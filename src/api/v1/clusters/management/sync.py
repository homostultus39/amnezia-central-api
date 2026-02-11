from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from datetime import datetime, timezone

from src.database.connection import SessionDep
from src.database.management.operations.cluster import get_cluster_by_id, update_last_handshake
from src.api.v1.clusters.logger import logger
from src.api.v1.clusters.schemas import ClusterSyncRequest, ClusterSyncResponse
from src.api.v1.deps.exceptions.cluster import ClusterNotFoundException, ClusterAuthException
from src.redis.management.cluster_status import ClusterStatusCache

router = APIRouter()
cache = ClusterStatusCache()


@router.post("/{cluster_id}/sync", response_model=ClusterSyncResponse)
async def sync_cluster(
    session: SessionDep,
    cluster_id: UUID,
    payload: ClusterSyncRequest,
    x_api_key: str = Header(...),
) -> ClusterSyncResponse:
    try:
        cluster = await get_cluster_by_id(session, cluster_id)
        if not cluster:
            logger.warning(f"Sync attempt for non-existent cluster: {cluster_id}")
            raise ClusterNotFoundException()

        if x_api_key != cluster.api_key:
            logger.warning(f"Invalid API key for cluster {cluster.name} ({cluster_id})")
            raise ClusterAuthException()

        await update_last_handshake(session, cluster_id)

        cluster_id_str = str(cluster_id)
        await cache.save_protocol(cluster_id_str, payload.protocol)

        traffic_data = {
            "total_rx_bytes": payload.server_traffic.total_rx_bytes,
            "total_tx_bytes": payload.server_traffic.total_tx_bytes,
            "total_peers": payload.server_traffic.total_peers,
            "online_peers": payload.server_traffic.online_peers,
        }
        await cache.save_traffic(cluster_id_str, traffic_data)

        for peer in payload.peers:
            peer_data = {
                "public_key": peer.public_key,
                "endpoint": peer.endpoint,
                "allowed_ips": peer.allowed_ips,
                "last_handshake": peer.last_handshake.isoformat(),
                "rx_bytes": peer.rx_bytes,
                "tx_bytes": peer.tx_bytes,
                "online": peer.online,
                "persistent_keepalive": peer.persistent_keepalive,
            }
            await cache.save_peer_status(cluster_id_str, peer.public_key, peer_data)

        logger.info(
            f"Synced cluster {cluster.name}: {payload.server_traffic.total_peers} peers, "
            f"{payload.server_traffic.online_peers} online"
        )

        return ClusterSyncResponse(
            status="synced",
            timestamp=datetime.now(timezone.utc),
        )

    except (ClusterNotFoundException, ClusterAuthException):
        raise
    except Exception as e:
        logger.error(f"Error syncing cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync cluster",
        )
