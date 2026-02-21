import pytz
from datetime import datetime

from src.database.connection import sessionmaker
from src.database.management.operations.client import get_all_clients
from src.database.management.operations.peer import get_peers_by_client_id
from src.database.management.operations.cluster import get_cluster_by_id
from src.api.v1.management.http_client import ClusterAPIClient
from src.management.logger import configure_logger
from src.management.settings import get_settings
from src.database.models import SubscriptionStatus

logger = configure_logger("CLEANUP_TASK", "red")
settings = get_settings()


async def cleanup_expired_clients():
    if not settings.subscription_enabled:
        logger.info("Subscription system is disabled, skipping cleanup")
        return

    logger.info("Starting cleanup of expired clients")

    async with sessionmaker() as session:
        try:
            clients = await get_all_clients(session)
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)

            expired_count = 0

            for client in clients:
                if client.expires_at is None:
                    continue

                if client.expires_at.astimezone(tz) < now and client.subscription_status != SubscriptionStatus.EXPIRED.value:
                    logger.info(f"Client subscription expired: {client.username} (expires_at: {client.expires_at})")

                    peers = await get_peers_by_client_id(session, client.id)

                    for peer in peers:
                        try:
                            cluster = await get_cluster_by_id(session, peer.cluster_id)
                            if not cluster:
                                logger.error(f"Cluster not found for peer {peer.id}: {peer.cluster_id}")
                                continue
                            cluster_client = ClusterAPIClient(cluster.endpoint, cluster.api_key)
                            await cluster_client.delete_peer(peer.public_key)
                            logger.info(f"Peer deleted from cluster: {peer.public_key} on {cluster.name}")
                        except Exception as e:
                            logger.error(f"Failed to delete peer {peer.id} from cluster: {e}")

                        try:
                            await session.delete(peer)
                        except Exception as e:
                            logger.error(f"Failed to delete peer {peer.id} from database: {e}")

                    if client.subscription_status == SubscriptionStatus.TRIAL.value:
                        client.trial_used = True

                    client.subscription_status = SubscriptionStatus.EXPIRED.value

                    await session.commit()
                    await session.refresh(client)

                    logger.info(f"Client subscription expired and peers deleted: {client.username} ({client.id})")
                    expired_count += 1

            logger.info(f"Cleanup completed. Processed {expired_count} expired clients")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
