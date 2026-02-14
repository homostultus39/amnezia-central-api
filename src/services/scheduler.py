import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.management.logger import configure_logger
from src.management.settings import get_settings

logger = configure_logger("SCHEDULER", "yellow")
settings = get_settings()

scheduler = AsyncIOScheduler(timezone=pytz.timezone(settings.timezone))


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
