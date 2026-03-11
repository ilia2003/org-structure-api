from functools import lru_cache
from pathlib import Path
from typing import Final

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.logger import CustomLogger


class _Settings(BaseSettings):
    """General service settings."""

    ROOT_DIR: Path = Path(__file__).parent.parent
    APP_DIR: Path = ROOT_DIR / "app"

    APP_TITLE: str = "Organizational Structure API"
    APP_DESCRIPTION: str = """
API for managing organizational departments and employees.

Features:
- create departments
- create employees inside departments
- retrieve department tree with nested children
- move departments in tree
- delete departments with cascade or employee reassignment
"""
    APP_RELEASE: str = "0.1.0"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def POSTGRES_URL(self) -> str:
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )

    @staticmethod
    def configure_logging():
        """Configure level and format of logging."""
        return CustomLogger.make_logger()

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )


@lru_cache
def get_settings(env_file: str = ".env") -> _Settings:
    return _Settings(_env_file=env_file)


SETTINGS: Final[_Settings] = get_settings()
