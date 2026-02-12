import uuid
from pydantic import BaseModel
from datetime import datetime

from src.database.models import AppType


class CreatePeerRequest(BaseModel):
    cluster_id: uuid.UUID
    client_id: uuid.UUID
    app_type: AppType
    protocol: str


class ClusterPeerResponse(BaseModel):
    public_key: str
    private_key: str
    allocated_ip: str
    endpoint: str
    config: str


class UpdatePeerRequest(BaseModel):
    app_type: AppType | None = None
    protocol: str | None = None


class PeerResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    cluster_id: uuid.UUID
    public_key: str
    allocated_ip: str
    endpoint: str
    app_type: str
    protocol: str
    created_at: datetime
    updated_at: datetime
    config: str | None = None
    config_download_url: str | None = None

    class Config:
        from_attributes = True


class PeerWithStatsResponse(PeerResponse):
    last_handshake: datetime | None = None
    rx_bytes: int | None = None
    tx_bytes: int | None = None
    online: bool | None = None
    persistent_keepalive: int | None = None
