from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.client import get_client_by_id, get_all_clients
from src.api.v1.clients.logger import logger
from src.api.v1.clients.schemas import ClientWithPeersResponse
from src.api.v1.management.exceptions.client import ClientNotFoundException

router = APIRouter()


@router.get("/", response_model=list[ClientWithPeersResponse])
async def list_clients(session: SessionDep) -> list[ClientWithPeersResponse]:
    try:
        clients = await get_all_clients(session)
        result = []

        for client in clients:
            response = ClientWithPeersResponse.model_validate(client)
            response.peers_count = len(client.peers)
            result.append(response)

        logger.info(f"Retrieved {len(result)} clients")
        return result

    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list clients",
        )


@router.get("/{client_id}", response_model=ClientWithPeersResponse)
async def get_client(
    session: SessionDep,
    client_id: UUID,
) -> ClientWithPeersResponse:
    try:
        client = await get_client_by_id(session, client_id)
        if not client:
            raise ClientNotFoundException()

        response = ClientWithPeersResponse.model_validate(client)
        response.peers_count = len(client.peers)

        logger.info(f"Retrieved client: {client.username}")
        return response

    except ClientNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get client",
        )
