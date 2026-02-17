from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.database.connection import SessionDep
from src.database.management.operations.tariff import create_tariff, get_tariff_by_code
from src.api.v1.tariffs.schemas import CreateTariffRequest, TariffResponse
from src.api.v1.tariffs.logger import logger

router = APIRouter()


@router.post("/", response_model=TariffResponse, status_code=status.HTTP_201_CREATED)
async def create_tariff_endpoint(
    session: SessionDep,
    payload: CreateTariffRequest,
) -> TariffResponse:
    try:
        existing = await get_tariff_by_code(session, payload.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tariff with code '{payload.code}' already exists"
            )

        tariff = await create_tariff(
            session,
            code=payload.code,
            name=payload.name,
            days=payload.days,
            price_rub=payload.price_rub,
            price_stars=payload.price_stars,
            is_active=payload.is_active,
            sort_order=payload.sort_order
        )

        logger.info(f"Tariff created: {tariff.code} - {tariff.name}")
        return TariffResponse.model_validate(tariff)

    except HTTPException:
        raise
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tariff with this code already exists"
        )
    except Exception as e:
        logger.error(f"Error creating tariff: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tariff"
        )
