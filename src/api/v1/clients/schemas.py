from pydantic import BaseModel
from datetime import datetime


class CreateClientRequest(BaseModel):
    username: str
    expires_at: datetime


class UpdateClientRequest(BaseModel):
    expires_at: datetime


class ClientResponse(BaseModel):
    id: str
    username: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientWithPeersResponse(ClientResponse):
    peers_count: int = 0
