from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from datetime import datetime, timezone

from src.database.connection import SessionDep
from src.database.management.operations.cluster import (
    get_cluster_by_id,
    update_cluster_runtime,
    update_last_handshake,
)
from src.api.v1.clusters.logger import logger
from src.api.v1.clusters.schemas import ClusterSyncRequest, ClusterSyncResponse
from src.api.v1.deps.exceptions.cluster import ClusterNotFoundException, ClusterAuthException
from src.api.v1.management.http_client import ClusterAPIClient
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
        runtime_protocol = payload.protocol
        runtime_container_name = payload.container_name or cluster.container_name
        runtime_container_status = payload.container_status or cluster.container_status

        if runtime_container_name is None or runtime_container_status is None:
            try:
                client = ClusterAPIClient(cluster.endpoint, cluster.api_key)
                server_status = await client.get_server_status()
                runtime_container_name = runtime_container_name or server_status.get("container_name")
                runtime_container_status = runtime_container_status or server_status.get("status")
                runtime_protocol = server_status.get("protocol") or runtime_protocol
            except Exception as exc:
                logger.warning(f"Failed to fetch server status for cluster {cluster.name}: {exc}")

        traffic_data = {
            "total_rx_bytes": payload.server_traffic.total_rx_bytes,
            "total_tx_bytes": payload.server_traffic.total_tx_bytes,
            "total_peers": payload.server_traffic.total_peers,
            "online_peers": payload.server_traffic.online_peers,
        }
        db_runtime_changed = await update_cluster_runtime(
            session=session,
            cluster_id=cluster_id,
            container_name=runtime_container_name,
            container_status=runtime_container_status,
            protocol=runtime_protocol,
            peers_count=payload.server_traffic.total_peers,
            online_peers_count=payload.server_traffic.online_peers,
        )
        protocol_cache_changed = await cache.save_protocol_if_changed(cluster_id_str, runtime_protocol)
        traffic_cache_changed = await cache.save_traffic_if_changed(cluster_id_str, traffic_data)

        peer_cache_updates = 0
        for peer in payload.peers:
            peer_data = {
                "public_key": peer.public_key,
                "endpoint": peer.endpoint,
                "allowed_ips": peer.allowed_ips,
                "last_handshake": peer.last_handshake.isoformat() if peer.last_handshake else None,
                "rx_bytes": peer.rx_bytes,
                "tx_bytes": peer.tx_bytes,
                "online": peer.online,
                "persistent_keepalive": peer.persistent_keepalive,
            }
            if await cache.save_peer_status_if_changed(cluster_id_str, peer.public_key, peer_data):
                peer_cache_updates += 1

        logger.info(
            f"Synced cluster {cluster.name}: {payload.server_traffic.total_peers} peers, "
            f"{payload.server_traffic.online_peers} online, "
            f"db_runtime_changed={db_runtime_changed}, "
            f"protocol_cache_changed={protocol_cache_changed}, "
            f"traffic_cache_changed={traffic_cache_changed}, "
            f"peer_cache_updates={peer_cache_updates}"
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
