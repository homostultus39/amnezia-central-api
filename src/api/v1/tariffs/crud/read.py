from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.tariff import get_tariff_by_id, get_all_tariffs, get_active_tariffs
from src.api.v1.tariffs.schemas import TariffResponse, ActiveTariffsResponse
from src.management.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/", response_model=list[TariffResponse])
async def get_all_tariffs_endpoint(session: SessionDep) -> list[TariffResponse]:
    tariffs = await get_all_tariffs(session)
    return [TariffResponse.model_validate(t) for t in tariffs]


@router.get("/active", response_model=ActiveTariffsResponse)
async def get_active_tariffs_endpoint(session: SessionDep) -> ActiveTariffsResponse:
    tariffs = await get_active_tariffs(session)
    return ActiveTariffsResponse(
        enabled=settings.subscription_enabled,
        tariffs=[TariffResponse.model_validate(t) for t in tariffs]
    )


@router.get("/{tariff_id}", response_model=TariffResponse)
async def get_tariff_endpoint(session: SessionDep, tariff_id: UUID) -> TariffResponse:
    tariff = await get_tariff_by_id(session, tariff_id)
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff not found"
        )
    return TariffResponse.model_validate(tariff)
