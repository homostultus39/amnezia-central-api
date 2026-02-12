import json
from typing import Any

from src.redis.connection import get_redis
from src.management.logger import configure_logger
from src.management.settings import get_settings

logger = configure_logger("CLUSTER_CACHE", "blue")
settings = get_settings()


class ClusterStatusCache:
    async def save_peer_status(self, cluster_id: str, public_key: str, peer_data: dict[str, Any]) -> None:
        redis = await get_redis()
        key = f"cluster:{cluster_id}:peer:{public_key}:status"

        try:
            await redis.setex(key, settings.peer_status_ttl, json.dumps(peer_data, sort_keys=True))
            logger.debug(f"Saved peer status: {key}")
        except Exception as e:
            logger.error(f"Error saving peer status {key}: {e}")
            raise

    async def save_peer_status_if_changed(self, cluster_id: str, public_key: str, peer_data: dict[str, Any]) -> bool:
        redis = await get_redis()
        key = f"cluster:{cluster_id}:peer:{public_key}:status"

        try:
            payload = json.dumps(peer_data, sort_keys=True)
            existing = await redis.get(key)
            if existing == payload:
                return False
            await redis.setex(key, settings.peer_status_ttl, payload)
            logger.debug(f"Saved peer status: {key}")
            return True
        except Exception as e:
            logger.error(f"Error saving peer status {key}: {e}")
            raise

    async def get_peer_status(self, cluster_id: str, public_key: str) -> dict[str, Any] | None:
        redis = await get_redis()
        key = f"cluster:{cluster_id}:peer:{public_key}:status"

        try:
            data = await redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting peer status {key}: {e}")
            return None

    async def get_all_peers_status(self, cluster_id: str) -> list[dict[str, Any]]:
        redis = await get_redis()
        pattern = f"cluster:{cluster_id}:peer:*:status"

        try:
            keys = await redis.keys(pattern)
            peers = []

            for key in keys:
                data = await redis.get(key)
                if data:
                    try:
                        peers.append(json.loads(data))
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode peer data from key: {key}")

            logger.debug(f"Retrieved {len(peers)} peers for cluster {cluster_id}")
            return peers
        except Exception as e:
            logger.error(f"Error getting all peers status for cluster {cluster_id}: {e}")
            return []

    async def save_traffic(self, cluster_id: str, traffic_data: dict[str, Any]) -> None:
        redis = await get_redis()
        key = f"cluster:{cluster_id}:traffic"

        try:
            await redis.setex(key, settings.peer_status_ttl, json.dumps(traffic_data, sort_keys=True))
            logger.debug(f"Saved traffic stats: {key}")
        except Exception as e:
            logger.error(f"Error saving traffic stats {key}: {e}")
            raise

    async def save_traffic_if_changed(self, cluster_id: str, traffic_data: dict[str, Any]) -> bool:
        redis = await get_redis()
        key = f"cluster:{cluster_id}:traffic"

        try:
            payload = json.dumps(traffic_data, sort_keys=True)
            existing = await redis.get(key)
            if existing == payload:
                return False
            await redis.setex(key, settings.peer_status_ttl, payload)
            logger.debug(f"Saved traffic stats: {key}")
            return True
        except Exception as e:
            logger.error(f"Error saving traffic stats {key}: {e}")
            raise

    async def get_traffic(self, cluster_id: str) -> dict[str, Any] | None:
        redis = await get_redis()
        key = f"cluster:{cluster_id}:traffic"

        try:
            data = await redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting traffic stats {key}: {e}")
            return None

    async def save_protocol(self, cluster_id: str, protocol: str) -> None:
        redis = await get_redis()
        key = f"cluster:{cluster_id}:protocol"

        try:
            await redis.setex(key, settings.peer_status_ttl, protocol)
            logger.debug(f"Saved protocol: {key}")
        except Exception as e:
            logger.error(f"Error saving protocol {key}: {e}")
            raise

    async def save_protocol_if_changed(self, cluster_id: str, protocol: str) -> bool:
        redis = await get_redis()
        key = f"cluster:{cluster_id}:protocol"

        try:
            existing = await redis.get(key)
            if existing == protocol:
                return False
            await redis.setex(key, settings.peer_status_ttl, protocol)
            logger.debug(f"Saved protocol: {key}")
            return True
        except Exception as e:
            logger.error(f"Error saving protocol {key}: {e}")
            raise

    async def get_protocol(self, cluster_id: str) -> str | None:
        redis = await get_redis()
        key = f"cluster:{cluster_id}:protocol"

        try:
            return await redis.get(key)
        except Exception as e:
            logger.error(f"Error getting protocol {key}: {e}")
            return None

    async def clear_cluster_cache(self, cluster_id: str) -> None:
        redis = await get_redis()
        pattern = f"cluster:{cluster_id}:*"

        try:
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries for cluster {cluster_id}")
        except Exception as e:
            logger.error(f"Error clearing cache for cluster {cluster_id}: {e}")
