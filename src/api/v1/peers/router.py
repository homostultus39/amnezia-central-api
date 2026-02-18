from fastapi import APIRouter

from src.api.v1.peers.crud import create, read, delete
from src.api.v1.peers.management import statistics

router = APIRouter()

router.include_router(create.router)
router.include_router(read.router)
router.include_router(delete.router)

router.include_router(statistics.router)
