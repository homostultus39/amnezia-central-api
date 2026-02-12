from fastapi import APIRouter

from src.api.v1.clusters.crud import create, read, update, delete
from src.api.v1.clusters.management import sync, restart

router = APIRouter()

router.include_router(create.router)
router.include_router(read.router)
router.include_router(update.router)
router.include_router(delete.router)
router.include_router(restart.router)

# Отдельный роутер для синхронизации, нужен для отдельного управления правами доступа
sync_router = APIRouter()
sync_router.include_router(sync.router)
