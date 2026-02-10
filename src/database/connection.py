from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.base import Base
from src.management.settings import get_settings


settings = get_settings()

engine = create_async_engine(
    url=settings.async_postgres_url,
    echo=False
)

sessionmaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with sessionmaker() as new_session:
        yield new_session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
