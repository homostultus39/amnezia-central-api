from minio import Minio
from minio.credentials import StaticProvider

from src.management.settings import get_settings


settings = get_settings()

minio_client = None


async def connect_minio():
    global minio_client
    minio_client = Minio(
        settings.minio_internal_host,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
        credentials=StaticProvider(
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key
        )
    )
    return minio_client


async def disconnect_minio():
    global minio_client
    minio_client = None


async def get_minio():
    return minio_client
