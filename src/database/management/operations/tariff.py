import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import TariffModel


async def get_tariff_by_id(session: AsyncSession, tariff_id: uuid.UUID) -> TariffModel | None:
    result = await session.execute(
        select(TariffModel).where(TariffModel.id == tariff_id)
    )
    return result.scalar_one_or_none()


async def get_tariff_by_code(session: AsyncSession, code: str) -> TariffModel | None:
    result = await session.execute(
        select(TariffModel).where(TariffModel.code == code)
    )
    return result.scalar_one_or_none()


async def get_all_tariffs(session: AsyncSession) -> list[TariffModel]:
    result = await session.execute(
        select(TariffModel).order_by(TariffModel.sort_order, TariffModel.created_at)
    )
    return result.scalars().all()


async def get_active_tariffs(session: AsyncSession) -> list[TariffModel]:
    result = await session.execute(
        select(TariffModel)
        .where(TariffModel.is_active == True)
        .order_by(TariffModel.sort_order, TariffModel.created_at)
    )
    return result.scalars().all()


async def create_tariff(
    session: AsyncSession,
    code: str,
    name: str,
    days: int,
    price_rub: int,
    price_stars: int,
    is_active: bool = True,
    sort_order: int = 0
) -> TariffModel:
    tariff = TariffModel(
        code=code,
        name=name,
        days=days,
        price_rub=price_rub,
        price_stars=price_stars,
        is_active=is_active,
        sort_order=sort_order
    )
    session.add(tariff)
    await session.commit()
    await session.refresh(tariff)
    return tariff


async def update_tariff(
    session: AsyncSession,
    tariff_id: uuid.UUID,
    name: str | None = None,
    days: int | None = None,
    price_rub: int | None = None,
    price_stars: int | None = None,
    is_active: bool | None = None,
    sort_order: int | None = None
) -> TariffModel | None:
    tariff = await get_tariff_by_id(session, tariff_id)
    if not tariff:
        return None

    if name is not None:
        tariff.name = name
    if days is not None:
        tariff.days = days
    if price_rub is not None:
        tariff.price_rub = price_rub
    if price_stars is not None:
        tariff.price_stars = price_stars
    if is_active is not None:
        tariff.is_active = is_active
    if sort_order is not None:
        tariff.sort_order = sort_order

    await session.commit()
    await session.refresh(tariff)
    return tariff


async def delete_tariff(session: AsyncSession, tariff_id: uuid.UUID) -> bool:
    tariff = await get_tariff_by_id(session, tariff_id)
    if not tariff:
        return False

    await session.delete(tariff)
    await session.commit()
    return True
