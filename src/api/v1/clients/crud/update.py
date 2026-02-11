from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.client import get_client_by_id, update_client
from src.api.v1.clients.logger import logger
from src.api.v1.clients.schemas import UpdateClientRequest, ClientResponse
from src.api.v1.deps.exceptions.client import ClientNotFoundException

router = APIRouter()


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client_endpoint(
    session: SessionDep,
    client_id: UUID,
    payload: UpdateClientRequest,
) -> ClientResponse:
    try:
        client = await get_client_by_id(session, client_id)
        if not client:
            raise ClientNotFoundException()

        updated_client = await update_client(
            session,
            client_id,
            expires_at=payload.expires_at,
        )

        logger.info(f"Client updated: {updated_client.username} ({client_id})")
        return ClientResponse.model_validate(updated_client)

    except ClientNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error updating client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update client",
        )
