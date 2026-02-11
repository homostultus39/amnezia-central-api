from pydantic import BaseModel
from datetime import datetime


class CreatePeerRequest(BaseModel):
    cluster_id: str
    client_id: str
    app_type: str
    protocol: str


class ClusterPeerResponse(BaseModel):
    """Response from cluster API when creating a peer"""
    public_key: str
    private_key: str
    allocated_ip: str
    endpoint: str


class UpdatePeerRequest(BaseModel):
    app_type: str | None = None
    protocol: str | None = None


class PeerResponse(BaseModel):
    id: str
    client_id: str
    cluster_id: str
    public_key: str
    allocated_ip: str
    endpoint: str
    app_type: str
    protocol: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PeerWithStatsResponse(PeerResponse):
    last_handshake: datetime | None = None
    rx_bytes: int | None = None
    tx_bytes: int | None = None
    online: bool | None = None
    persistent_keepalive: int | None = None
