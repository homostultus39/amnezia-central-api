from fastapi import APIRouter

from src.api.v1.peers.crud import create, read, update, delete
from src.api.v1.peers.management import statistics

router = APIRouter()

router.include_router(create.router, tags=["Peers"])
router.include_router(read.router, tags=["Peers"])
router.include_router(update.router, tags=["Peers"])
router.include_router(delete.router, tags=["Peers"])

router.include_router(statistics.router, tags=["Peers"])
