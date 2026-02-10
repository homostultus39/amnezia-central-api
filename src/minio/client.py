from io import BytesIO
from datetime import timedelta
from urllib.parse import quote

from src.minio.connection import get_minio
from src.management.settings import get_settings


settings = get_settings()


def _get_object_name(client_id: str) -> str:
    """Generate escaped object name for MinIO."""
    escaped_id = quote(str(client_id), safe="")
    return f"configs/{escaped_id}.conf"


async def upload_config(client_id: str, config_data: bytes) -> str:
    """Upload config to MinIO and return path."""
    minio = await get_minio()
    object_name = _get_object_name(client_id)

    minio.put_object(
        settings.minio_bucket,
        object_name,
        BytesIO(config_data),
        length=len(config_data),
        content_type="application/octet-stream"
    )

    return object_name


async def get_config_download_url(client_id: str) -> str:
    """Generate presigned URL for config download."""
    minio = await get_minio()
    object_name = _get_object_name(client_id)

    url = minio.get_presigned_download_url(
        settings.minio_bucket,
        object_name,
        expires=timedelta(seconds=settings.minio_presigned_expires_seconds)
    )

    return url.replace(settings.minio_internal_host, settings.minio_public_host)


async def delete_config(client_id: str) -> None:
    """Delete config from MinIO."""
    minio = await get_minio()
    object_name = _get_object_name(client_id)
    minio.remove_object(settings.minio_bucket, object_name)
