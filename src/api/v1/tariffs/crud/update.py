from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.tariff import update_tariff
from src.api.v1.tariffs.schemas import UpdateTariffRequest, TariffResponse
from src.api.v1.tariffs.logger import logger


router = APIRouter()


@router.patch("/{tariff_id}", response_model=TariffResponse)
async def update_tariff_endpoint(
    session: SessionDep,
    tariff_id: UUID,
    payload: UpdateTariffRequest,
) -> TariffResponse:
    try:
        tariff = await update_tariff(
            session,
            tariff_id,
            name=payload.name,
            days=payload.days,
            price_rub=payload.price_rub,
            price_stars=payload.price_stars,
            is_active=payload.is_active,
            sort_order=payload.sort_order
        )

        if not tariff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tariff not found"
            )

        logger.info(f"Tariff updated: {tariff.code} - {tariff.name}")
        return TariffResponse.model_validate(tariff)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tariff {tariff_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tariff"
        )
