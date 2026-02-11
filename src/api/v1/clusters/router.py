from fastapi import APIRouter

from src.api.v1.clusters.crud import create, read, update, delete
from src.api.v1.clusters.management import sync, restart

router = APIRouter()

router.include_router(create.router, tags=["Clusters"])
router.include_router(read.router, tags=["Clusters"])
router.include_router(update.router, tags=["Clusters"])
router.include_router(delete.router, tags=["Clusters"])

router.include_router(sync.router, tags=["Clusters"])
router.include_router(restart.router, tags=["Clusters"])
