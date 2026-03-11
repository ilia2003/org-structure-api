import sys
from enum import StrEnum

from loguru import logger as LOGGER


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CustomLogger:
    LOGGING_LEVEL = "DEBUG"

    LOGGING_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "<level>{message}</level>"
    )

    @classmethod
    def make_logger(cls):
        LOGGER.remove()
        LOGGER.add(
            sys.stdout,
            level=cls.LOGGING_LEVEL,
            format=cls.LOGGING_FORMAT,
        )
        return LOGGER
