import uuid
from pydantic import BaseModel, Field
from datetime import datetime


class CreateClientRequest(BaseModel):
    username: str


class UpdateClientRequest(BaseModel):
    expires_at: datetime


class SubscribeRequest(BaseModel):
    tariff_code: str = Field(..., pattern="^(30|90|180|360)$")


class ClientResponse(BaseModel):
    id: uuid.UUID
    username: str
    expires_at: datetime
    subscription_status: str
    trial_used: bool
    last_subscription_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientWithPeersResponse(ClientResponse):
    peers_count: int = 0
