from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from src.database.connection import SessionDep
from src.database.management.operations.tariff import delete_tariff, get_tariff_by_id
from src.api.v1.tariffs.logger import logger

router = APIRouter()


@router.delete("/{tariff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tariff_endpoint(session: SessionDep, tariff_id: UUID) -> None:
    try:
        tariff = await get_tariff_by_id(session, tariff_id)
        if not tariff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tariff not found"
            )

        success = await delete_tariff(session, tariff_id)
        if success:
            logger.info(f"Tariff deleted: {tariff.code} - {tariff.name}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tariff {tariff_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tariff"
        )
