import uuid
from src.api.v1.clusters.schemas import ClusterWithStatusResponse
from src.redis.management.cluster_status import ClusterStatusCache


cache = ClusterStatusCache()


async def enrich_cluster_status(
    response: ClusterWithStatusResponse,
    cluster_id: uuid.UUID,
) -> None:
    cluster_id_str = str(cluster_id)
    peers = await cache.get_all_peers_status(cluster_id_str)
    response.peers_count = len(peers)
    response.online_peers_count = sum(1 for p in peers if p.get("online", False))

    traffic = await cache.get_traffic(cluster_id_str)
    protocol = await cache.get_protocol(cluster_id_str)

    if traffic:
        response.container_status = "running"
    if protocol:
        response.protocol = protocol
