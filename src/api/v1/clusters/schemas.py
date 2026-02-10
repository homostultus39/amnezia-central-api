from pydantic import BaseModel
from datetime import datetime


class ClusterResponse(BaseModel):
    id: str
    name: str
    host: str
    port: int
    is_active: bool
    last_handshake: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
