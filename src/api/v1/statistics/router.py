from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.peer import get_peer_by_id
from src.database.management.operations.cluster import get_cluster_by_id, get_all_clusters
from src.database.management.operations.statistics import (
    get_clusters_counts,
    get_clients_counts,
    get_peers_counts,
    get_cluster_peers_counts,
    get_cluster_unique_clients_count,
)
from src.api.v1.statistics.logger import logger
from src.api.v1.statistics.schemas import (
    GlobalStatsResponse,
    ClusterStatsResponse,
    PeerWithStatsResponse,
    ClustersStats,
    ClientsStats,
    ClientsByStatus,
    PeersStats,
    PeersByAppType,
    TrafficStats,
    ClusterInfo,
    ClusterClientsStats,
)
from src.api.v1.management.exceptions.peer import PeerNotFoundException
from src.api.v1.management.exceptions.cluster import ClusterNotFoundException
from src.redis.management.cluster_status import ClusterStatusCache
from src.minio import MinioClient

router = APIRouter()
cache = ClusterStatusCache()
minio_client = MinioClient()


@router.get("/", response_model=GlobalStatsResponse)
async def get_global_statistics(session: SessionDep) -> GlobalStatsResponse:
    try:
        clusters_data = await get_clusters_counts(session)
        clients_data = await get_clients_counts(session)
        peers_data = await get_peers_counts(session)

        all_clusters = await get_all_clusters(session)
        total_online = sum(c.online_peers_count for c in all_clusters)

        total_rx = 0
        total_tx = 0
        has_traffic = False
        for cluster in all_clusters:
            traffic = await cache.get_traffic(str(cluster.id))
            if traffic:
                total_rx += traffic.get("total_rx_bytes", 0)
                total_tx += traffic.get("total_tx_bytes", 0)
                has_traffic = True

        by_status_raw = clients_data["by_status"]
        by_app_type_raw = peers_data["by_app_type"]

        response = GlobalStatsResponse(
            clusters=ClustersStats(
                total=clusters_data["total"],
                active=clusters_data["active"],
                inactive=clusters_data["inactive"],
            ),
            clients=ClientsStats(
                total=clients_data["total"],
                by_status=ClientsByStatus(
                    active=by_status_raw.get("active", 0),
                    trial=by_status_raw.get("trial", 0),
                    expired=by_status_raw.get("expired", 0),
                ),
            ),
            peers=PeersStats(
                total=peers_data["total"],
                online=total_online,
                by_app_type=PeersByAppType(
                    amnezia_vpn=by_app_type_raw.get("amnezia_vpn", 0),
                    amnezia_wg=by_app_type_raw.get("amnezia_wg", 0),
                ),
            ),
            traffic=TrafficStats(
                total_rx_bytes=total_rx if has_traffic else None,
                total_tx_bytes=total_tx if has_traffic else None,
            ),
        )

        logger.info("Global statistics retrieved")
        return response

    except Exception as e:
        logger.error(f"Error getting global statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get global statistics",
        )


@router.get("/clusters/{cluster_id}", response_model=ClusterStatsResponse)
async def get_cluster_statistics(
    session: SessionDep,
    cluster_id: UUID,
) -> ClusterStatsResponse:
    try:
        cluster = await get_cluster_by_id(session, cluster_id)
        if not cluster:
            raise ClusterNotFoundException()

        peers_data = await get_cluster_peers_counts(session, cluster_id)
        unique_clients = await get_cluster_unique_clients_count(session, cluster_id)

        traffic = await cache.get_traffic(str(cluster_id))

        by_app_type_raw = peers_data["by_app_type"]

        response = ClusterStatsResponse(
            cluster=ClusterInfo(
                id=cluster.id,
                name=cluster.name,
                protocol=cluster.protocol,
                container_status=cluster.container_status,
                is_active=cluster.is_active,
            ),
            clients=ClusterClientsStats(total=unique_clients),
            peers=PeersStats(
                total=peers_data["total"],
                online=cluster.online_peers_count,
                by_app_type=PeersByAppType(
                    amnezia_vpn=by_app_type_raw.get("amnezia_vpn", 0),
                    amnezia_wg=by_app_type_raw.get("amnezia_wg", 0),
                ),
            ),
            traffic=TrafficStats(
                total_rx_bytes=traffic.get("total_rx_bytes") if traffic else None,
                total_tx_bytes=traffic.get("total_tx_bytes") if traffic else None,
            ),
        )

        logger.info(f"Cluster statistics retrieved: {cluster.name}")
        return response

    except ClusterNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting cluster statistics {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cluster statistics",
        )


@router.get("/peers/{peer_id}", response_model=PeerWithStatsResponse)
async def get_peer_statistics(
    session: SessionDep,
    peer_id: UUID,
) -> PeerWithStatsResponse:
    try:
        peer = await get_peer_by_id(session, peer_id)
        if not peer:
            raise PeerNotFoundException()

        response = PeerWithStatsResponse.model_validate(peer)
        response.config = await minio_client.get_peer_config(peer.id)
        response.config_download_url = await minio_client.get_peer_config_url(peer.id)

        peer_status = await cache.get_peer_status(str(peer.cluster_id), peer.public_key)
        if peer_status:
            response.last_handshake = peer_status.get("last_handshake")
            response.rx_bytes = peer_status.get("rx_bytes")
            response.tx_bytes = peer_status.get("tx_bytes")
            response.online = peer_status.get("online")
            response.persistent_keepalive = peer_status.get("persistent_keepalive")
            logger.debug(f"Enriched peer stats from cache: {peer.public_key}")
        else:
            logger.warning(f"No cached stats for peer: {peer.public_key}, cluster: {peer.cluster_id}")

        logger.info(f"Peer statistics retrieved: {peer.public_key}")
        return response

    except PeerNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting peer statistics {peer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get peer statistics",
        )
