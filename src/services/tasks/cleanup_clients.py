import pytz
from datetime import datetime

from src.database.connection import async_sessionmaker
from src.database.management.operations.client import get_all_clients, delete_client
from src.database.management.operations.peer import get_peers_by_client_id
from src.api.v1.clusters.management.http_client import ClusterAPIClient
from src.management.logger import configure_logger
from src.management.settings import get_settings

logger = configure_logger("CLEANUP_TASK", "red")
settings = get_settings()


async def cleanup_expired_clients():
    logger.info("Starting cleanup of expired clients")

    async with async_sessionmaker() as session:
        try:
            clients = await get_all_clients(session)
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)

            expired_count = 0

            for client in clients:
                if client.expires_at.astimezone(tz) < now:
                    logger.info(f"Client expired: {client.username} (expires_at: {client.expires_at})")

                    peers = await get_peers_by_client_id(session, client.id)

                    for peer in peers:
                        try:
                            cluster_client = ClusterAPIClient(peer.cluster.endpoint, peer.cluster.api_key)
                            await cluster_client.delete_peer(peer.id)
                            logger.info(f"Peer deleted from cluster: {peer.public_key} on {peer.cluster.name}")
                        except Exception as e:
                            logger.error(f"Failed to delete peer {peer.id} from cluster: {e}")

                    await delete_client(session, client.id)
                    logger.info(f"Client deleted: {client.username} ({client.id})")
                    expired_count += 1

            logger.info(f"Cleanup completed. Deleted {expired_count} expired clients")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
