import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel



class PeerWithStatsResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    cluster_id: uuid.UUID
    protocol: str
    app_type: str
    last_handshake: Optional[datetime] = None
    rx_bytes: Optional[int] = None
    tx_bytes: Optional[int] = None
    online: Optional[bool] = None

    class Config:
        from_attributes = True



class ClustersStats(BaseModel):
    total: int
    active: int
    inactive: int


class ClientsByStatus(BaseModel):
    active: int = 0
    trial: int = 0
    expired: int = 0


class ClientsStats(BaseModel):
    total: int
    by_status: ClientsByStatus


class PeersByAppType(BaseModel):
    amnezia_vpn: int = 0
    amnezia_wg: int = 0


class PeersStats(BaseModel):
    total: int
    online: int
    by_app_type: PeersByAppType


class TrafficStats(BaseModel):
    total_rx_bytes: Optional[int] = None
    total_tx_bytes: Optional[int] = None


class GlobalStatsResponse(BaseModel):
    clusters: ClustersStats
    clients: ClientsStats
    peers: PeersStats
    traffic: TrafficStats



class ClusterInfo(BaseModel):
    id: uuid.UUID
    name: str
    protocol: Optional[str]
    container_status: Optional[str]
    is_active: bool


class ClusterClientsStats(BaseModel):
    total: int


class ClusterStatsResponse(BaseModel):
    cluster: ClusterInfo
    clients: ClusterClientsStats
    peers: PeersStats
    traffic: TrafficStats
