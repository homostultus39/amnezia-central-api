from functools import lru_cache
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    development: bool

    admin_username: str
    admin_password: str

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str

    redis_password: str
    redis_host: str
    redis_port: int
    redis_db: int = 0

    minio_internal_host: str
    minio_public_host: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "amnezia-configs"
    minio_secure: bool = False
    minio_presigned_expires_seconds: int = 3600

    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_minutes: int = 43200
    jwt_blacklist_ex: int = 3600
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    peer_status_ttl: int = 120
    cluster_api_timeout: int = 10
    timezone: str = "Europe/Moscow"
    cleanup_schedule_hour: int = 3
    cleanup_schedule_minute: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def async_postgres_url(self) -> str:
        encoded_password = quote_plus(self.postgres_password)
        return f"postgresql+asyncpg://{self.postgres_user}:{encoded_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def sync_postgres_url(self) -> str:
        encoded_password = quote_plus(self.postgres_password)
        return f"postgresql+psycopg2://{self.postgres_user}:{encoded_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def cookie_secure(self) -> bool:
        return not self.development

    @property
    def cookie_samesite(self) -> str:
        return "lax" if self.development else "strict"


@lru_cache
def get_settings():
    return Settings()
