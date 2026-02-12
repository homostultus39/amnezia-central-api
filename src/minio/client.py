import asyncio
import io
from datetime import timedelta
from typing import Optional
from uuid import UUID

from minio.error import S3Error

from src.management.logger import configure_logger
from src.management.settings import get_settings
from src.minio.connection import get_minio_client, get_minio_public_client

settings = get_settings()
logger = configure_logger("MinioClient", "cyan")


class MinioClient:
    def __init__(self) -> None:
        self._client = get_minio_client()
        self._public_client = get_minio_public_client()
        self._bucket_ready = False
        self.bucket_name = settings.minio_bucket

    async def _run(self, func, *args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    async def _ensure_bucket(self) -> None:
        if self._bucket_ready:
            return
        exists = await self._run(self._client.bucket_exists, self.bucket_name)
        if not exists:
            await self._run(self._client.make_bucket, self.bucket_name)
        self._bucket_ready = True

    async def upload_text(
        self,
        object_name: str,
        content: str,
        content_type: str = "text/plain",
    ) -> None:
        await self._ensure_bucket()
        data = content.encode()
        await self._run(
            self._client.put_object,
            self.bucket_name,
            object_name,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        logger.info(f"Text object '{object_name}' uploaded to '{self.bucket_name}'")

    async def upload_bytes(
        self,
        object_name: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> None:
        await self._ensure_bucket()
        await self._run(
            self._client.put_object,
            self.bucket_name,
            object_name,
            io.BytesIO(content),
            length=len(content),
            content_type=content_type,
        )
        logger.info(f"Bytes object '{object_name}' uploaded to '{self.bucket_name}'")

    async def get_text(self, object_name: str, encoding: str = "utf-8") -> str:
        await self._ensure_bucket()

        def _read_object() -> bytes:
            response = self._client.get_object(self.bucket_name, object_name)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        data = await self._run(_read_object)
        return data.decode(encoding)

    async def delete_object(self, object_name: str) -> None:
        await self._ensure_bucket()
        await self._run(self._client.remove_object, self.bucket_name, object_name)
        logger.info(f"Object '{object_name}' deleted from '{self.bucket_name}'")

    async def presigned_get_url(
        self,
        object_name: str,
        expires_seconds: Optional[int] = None,
    ) -> str:
        expires = timedelta(
            seconds=expires_seconds or settings.minio_presigned_expires_seconds
        )

        presigned_url = await self._run(
            self._public_client.presigned_get_object,
            self.bucket_name,
            object_name,
            expires=expires,
        )

        logger.debug(f"Generated presigned URL for '{object_name}'")
        return presigned_url

    async def is_available(self) -> bool:
        try:
            await self._ensure_bucket()
        except S3Error:
            return False
        return True

    @staticmethod
    def _peer_config_key(peer_id: UUID) -> str:
        return f"peers/{peer_id}.conf"

    async def save_peer_config(self, peer_id: UUID, config: str) -> str:
        object_name = self._peer_config_key(peer_id)
        await self.upload_text(object_name, config, content_type="text/plain")
        return await self.presigned_get_url(object_name)

    async def get_peer_config(self, peer_id: UUID) -> str | None:
        object_name = self._peer_config_key(peer_id)
        try:
            return await self.get_text(object_name)
        except S3Error as exc:
            if exc.code in {"NoSuchKey", "NoSuchObject"}:
                return None
            raise

    async def get_peer_config_url(self, peer_id: UUID) -> str | None:
        object_name = self._peer_config_key(peer_id)
        try:
            return await self.presigned_get_url(object_name)
        except S3Error as exc:
            if exc.code in {"NoSuchKey", "NoSuchObject"}:
                return None
            raise

    async def delete_peer_config(self, peer_id: UUID) -> None:
        object_name = self._peer_config_key(peer_id)
        try:
            await self.delete_object(object_name)
        except S3Error as exc:
            if exc.code in {"NoSuchKey", "NoSuchObject"}:
                return
            raise
