from pydantic import BaseModel
from datetime import datetime


class ClientResponse(BaseModel):
    id: str
    username: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
