from minio import Minio
from urllib.parse import urlparse

from src.management.settings import get_settings

settings = get_settings()

_minio_client: Minio | None = None
_minio_public_client: Minio | None = None


def get_minio_client() -> Minio:
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            settings.minio_internal_host,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
    return _minio_client


def get_minio_public_client() -> Minio:
    global _minio_public_client
    if _minio_public_client is None:
        host_str = settings.minio_public_host
        parsed = urlparse(host_str if '://' in host_str else f'http://{host_str}')

        is_secure = parsed.scheme == 'https'
        public_endpoint = parsed.netloc

        _minio_public_client = Minio(
            public_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=is_secure,
            region="us-east-1",
        )
    return _minio_public_client
