from fastapi import APIRouter

from src.api.v1.peers.crud import create, read, delete

router = APIRouter()

router.include_router(create.router)
router.include_router(read.router)
router.include_router(delete.router)
