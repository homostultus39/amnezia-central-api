import uuid
from datetime import datetime, timezone

from src.api.v1.clusters.schemas import ClusterWithStatusResponse
from src.management.settings import get_settings
from src.redis.management.cluster_status import ClusterStatusCache


cache = ClusterStatusCache()
settings = get_settings()


async def enrich_cluster_status(
    response: ClusterWithStatusResponse,
    cluster_id: uuid.UUID,
) -> None:
    cluster_id_str = str(cluster_id)
    traffic = await cache.get_traffic(cluster_id_str)
    protocol = await cache.get_protocol(cluster_id_str)

    if traffic is not None:
        response.peers_count = traffic.get("total_peers", response.peers_count)
        response.online_peers_count = traffic.get("online_peers", response.online_peers_count)

    if protocol:
        response.protocol = protocol

    if response.container_status is None:
        response.container_status = "unknown"

    if response.last_handshake is not None:
        last_handshake = response.last_handshake
        if last_handshake.tzinfo is None:
            last_handshake = last_handshake.replace(tzinfo=timezone.utc)
        age_seconds = (datetime.now(timezone.utc) - last_handshake).total_seconds()
        if age_seconds > settings.peer_status_ttl and response.container_status == "running":
            response.container_status = "stale"
    elif response.container_status == "running":
        response.container_status = "stale"
