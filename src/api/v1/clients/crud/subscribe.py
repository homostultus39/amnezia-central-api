from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.client import get_client_by_id, subscribe_client
from src.database.management.operations.peer import get_peers_by_client_id
from src.database.management.operations.cluster import get_cluster_by_id
from src.api.v1.clients.logger import logger
from src.api.v1.clients.schemas import SubscribeRequest, ClientResponse
from src.api.v1.management.exceptions.client import ClientNotFoundException
from src.api.v1.management.http_client import ClusterAPIClient
from src.database.models import SubscriptionStatus

router = APIRouter()


@router.post("/{client_id}/subscribe", response_model=ClientResponse)
async def subscribe_client_endpoint(
    session: SessionDep,
    client_id: UUID,
    payload: SubscribeRequest,
) -> ClientResponse:
    try:
        client = await get_client_by_id(session, client_id)
        if not client:
            raise ClientNotFoundException()

        should_delete_peers = (
            client.subscription_status == SubscriptionStatus.EXPIRED.value or
            client.subscription_status == SubscriptionStatus.TRIAL.value
        )

        if should_delete_peers:
            peers = await get_peers_by_client_id(session, client_id)

            for peer in peers:
                try:
                    cluster = await get_cluster_by_id(session, peer.cluster_id)
                    if cluster:
                        cluster_client = ClusterAPIClient(cluster.endpoint, cluster.api_key)
                        await cluster_client.delete_peer(peer.public_key)
                        logger.info(f"Peer deleted from cluster during subscription: {peer.public_key}")
                except Exception as e:
                    logger.warning(f"Failed to delete peer {peer.id} from cluster (may already be deleted): {e}")

        updated_client = await subscribe_client(session, client_id, payload.tariff_code)

        logger.info(f"Client subscribed: {updated_client.username} ({client_id}) - tariff: {payload.tariff_code}")
        return ClientResponse.model_validate(updated_client)

    except ClientNotFoundException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in subscribe_client_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error subscribing client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to subscribe client",
        )
