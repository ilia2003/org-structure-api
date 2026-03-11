import asyncio

import asyncpg
from loguru import logger as LOGGER

from app.settings import get_settings


class DatabaseManager:
    def __init__(self):
        self.config = get_settings()

    def get_postgres_dsn(self) -> str:
        """Generate DSN for connecting to PostgreSQL."""
        return "postgresql://{}:{}@{}:{}/postgres".format(
            self.config.POSTGRES_USER,
            self.config.POSTGRES_PASSWORD,
            self.config.POSTGRES_HOST,
            self.config.POSTGRES_PORT,
        )

    async def create_database(self) -> None:
        """Create database and grant permissions."""
        try:
            async with asyncpg.create_pool(dsn=self.get_postgres_dsn()) as pool:
                async with pool.acquire() as conn:
                    await conn.execute(f"CREATE DATABASE {self.config.POSTGRES_DB}")
                    await conn.execute(
                        f"GRANT ALL PRIVILEGES ON DATABASE {self.config.POSTGRES_DB} TO {self.config.POSTGRES_USER}"
                    )
                    LOGGER.info(f"Database created: {self.config.POSTGRES_DB}")
        except asyncpg.exceptions.DuplicateDatabaseError:
            LOGGER.warning(f"Database already exists: {self.config.POSTGRES_DB}")

    async def drop_database(self) -> None:
        """Drop database."""
        try:
            async with asyncpg.create_pool(dsn=self.get_postgres_dsn()) as pool:
                async with pool.acquire() as conn:
                    await conn.execute(f"DROP DATABASE {self.config.POSTGRES_DB}")
                    LOGGER.info(f"Database dropped: {self.config.POSTGRES_DB}")
        except Exception as e:
            LOGGER.warning(f"Failed to drop database {self.config.POSTGRES_DB}: {e}")


def main_create() -> None:
    db = DatabaseManager()
    asyncio.run(db.create_database())


def main_drop() -> None:
    db = DatabaseManager()
    asyncio.run(db.drop_database())
