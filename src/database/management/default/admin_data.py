from src.database.connection import sessionmaker
from src.database.management.operations.admin import get_admin_by_username, create_admin
from src.management.logger import configure_logger
from src.management.settings import get_settings

logger = configure_logger("ADMIN_DATA", "blue")
settings = get_settings()


async def create_default_admin_user():
    """Create default admin user if not exists."""
    async with sessionmaker() as session:
        existing_admin = await get_admin_by_username(session, settings.admin_username)
        if not existing_admin:
            await create_admin(session, settings.admin_username, settings.admin_password)
            logger.info(f"Default admin user '{settings.admin_username}' created")
        else:
            logger.info(f"Admin user '{settings.admin_username}' already exists")
