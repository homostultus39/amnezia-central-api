import uuid
from pydantic import BaseModel
from datetime import datetime


class CreateClusterRequest(BaseModel):
    name: str
    endpoint: str
    api_key: str


class UpdateClusterRequest(BaseModel):
    name: str | None = None
    endpoint: str | None = None
    api_key: str | None = None
    is_active: bool | None = None


class PeerStatusUpdate(BaseModel):
    public_key: str
    endpoint: str
    allowed_ips: list[str]
    last_handshake: datetime
    rx_bytes: int
    tx_bytes: int
    online: bool
    persistent_keepalive: int


class ServerTrafficUpdate(BaseModel):
    total_rx_bytes: int
    total_tx_bytes: int
    total_peers: int
    online_peers: int


class ClusterSyncRequest(BaseModel):
    protocol: str
    peers: list[PeerStatusUpdate]
    server_traffic: ServerTrafficUpdate
    sync_timestamp: datetime


class ClusterResponse(BaseModel):
    id: uuid.UUID
    name: str
    endpoint: str
    is_active: bool
    last_handshake: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClusterWithStatusResponse(ClusterResponse):
    container_status: str | None = None
    container_name: str | None = None
    protocol: str | None = None
    peers_count: int | None = None
    online_peers_count: int | None = None


class RestartClusterResponse(BaseModel):
    cluster_id: uuid.UUID
    status: str
    message: str


class ClusterSyncResponse(BaseModel):
    status: str
    timestamp: datetime
