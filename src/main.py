from contextlib import asynccontextmanager
from fastapi import FastAPI
from alembic import command
from alembic.config import Config

from src.management.logger import configure_logger
from src.redis.connection import connect_redis, disconnect_redis
from src.minio.connection import connect_minio, disconnect_minio
from src.database.management.default.admin_data import create_default_admin_user


logger = configure_logger("MAIN", "cyan")


def run_migrations():
    logger.info("Running migrations...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Migrations applied successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    logger.info("Connecting to Redis...")
    await connect_redis()
    logger.info("Redis connected successfully.")
    logger.info("Connecting to MinIO...")
    await connect_minio()
    logger.info("MinIO connected successfully.")
    logger.info("Creating default admin user...")
    await create_default_admin_user()
    logger.info("Default admin user created successfully.")
    logger.info("Initialization completed successfully.")
    yield
    logger.info("Disconnecting from Redis...")
    await disconnect_redis()
    logger.info("Redis disconnected.")
    logger.info("Disconnecting from MinIO...")
    await disconnect_minio()
    logger.info("MinIO disconnected.")


app = FastAPI(
    title="Amnezia Central API",
    version="0.1.0",
    lifespan=lifespan,
    root_path="/api/v1",
    swagger_ui_parameters={"persistAuthorization": True},
)


@app.get("/health")
async def health_check():
    return {
        "app": "Amnezia Central API",
        "status": "running"
    }
