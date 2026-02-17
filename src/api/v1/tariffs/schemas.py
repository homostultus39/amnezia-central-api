import uuid
from pydantic import BaseModel, Field
from datetime import datetime


class CreateTariffRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    days: int = Field(..., gt=0)
    price_rub: int = Field(..., ge=0)
    price_stars: int = Field(..., ge=0)
    is_active: bool = True
    sort_order: int = 0


class UpdateTariffRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    days: int | None = Field(None, gt=0)
    price_rub: int | None = Field(None, ge=0)
    price_stars: int | None = Field(None, ge=0)
    is_active: bool | None = None
    sort_order: int | None = None


class TariffResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    days: int
    price_rub: int
    price_stars: int
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActiveTariffsResponse(BaseModel):
    enabled: bool
    tariffs: list[TariffResponse]
