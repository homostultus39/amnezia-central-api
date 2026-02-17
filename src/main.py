from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from alembic import command
from alembic.config import Config

from src.management.logger import configure_logger
from src.database.management.default.admin_data import create_default_admin_user
from src.api.v1.auth.router import router as auth_router
from src.api.v1.clients.router import router as clients_router
from src.api.v1.clusters.router import router as clusters_router, sync_router as clusters_sync_router
from src.api.v1.peers.router import router as peers_router
from src.api.v1.tariffs.router import router as tariffs_router
from src.api.v1.management.middlewares.auth import get_current_admin
from src.services.scheduler import scheduler, start_scheduler, stop_scheduler
from src.services.tasks.cleanup_clients import cleanup_expired_clients
from src.management.settings import get_settings

logger = configure_logger("MAIN", "cyan")
settings = get_settings()


def run_migrations():
    logger.info("Running migrations...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Migrations applied successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    logger.info("Creating default admin user...")
    await create_default_admin_user()

    scheduler.add_job(
        cleanup_expired_clients,
        trigger="cron",
        hour=settings.cleanup_schedule_hour,
        minute=settings.cleanup_schedule_minute,
        id="cleanup_expired_clients",
        replace_existing=True,
    )
    start_scheduler()

    logger.info("Application initialized successfully.")
    yield

    stop_scheduler()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="Amnezia Central API",
    version="0.1.0",
    lifespan=lifespan,
    root_path="/api/v1",
    docs_url="/docs" if settings.development else None,
    redoc_url="/redoc" if settings.development else None,
    openapi_url="/openapi.json" if settings.development else None,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
)

app.include_router(
    clients_router,
    prefix="/clients",
    tags=["Clients"],
    dependencies=[Depends(get_current_admin)]
)

app.include_router(
    clusters_router,
    prefix="/clusters",
    tags=["Clusters"],
    dependencies=[Depends(get_current_admin)]
)

app.include_router(
    clusters_sync_router,
    prefix="/clusters",
    tags=["Clusters"]
)

app.include_router(
    peers_router,
    prefix="/peers",
    tags=["Peers"],
    dependencies=[Depends(get_current_admin)]
)

app.include_router(
    tariffs_router,
    prefix="/tariffs",
    tags=["Tariffs"],
    dependencies=[Depends(get_current_admin)]
)


@app.get("/health")
async def health_check():
    return {
        "app": "Amnezia Central API",
        "status": "running"
    }
