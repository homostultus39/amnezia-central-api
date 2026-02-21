from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.client import get_client_by_username, create_client
from src.api.v1.clients.logger import logger
from src.api.v1.clients.schemas import CreateClientRequest, ClientResponse

router = APIRouter()


@router.post("/", response_model=ClientResponse)
async def create_client_endpoint(
    session: SessionDep,
    payload: CreateClientRequest,
) -> ClientResponse:
    try:
        existing_client = await get_client_by_username(session, payload.username)
        if existing_client:
            logger.warning(f"Attempted to create client with existing username: {payload.username}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Client with this username already exists",
            )

        client = await create_client(
            session,
            username=payload.username,
            is_admin=payload.is_admin
        )

        logger.info(f"Client created: {client.username} ({client.id})")
        return ClientResponse.model_validate(client)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create client",
        )
