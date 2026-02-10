from pydantic import BaseModel
from datetime import datetime


class PeerResponse(BaseModel):
    id: str
    client_id: str
    public_key: str
    allocated_ip: str
    endpoint: str
    app_type: str
    protocol: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
