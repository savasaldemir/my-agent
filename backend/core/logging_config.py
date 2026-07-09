"""Logging configuration"""

import sys
from loguru import logger


def setup_logging(log_level: str = "INFO") -> None:
    """Configure loguru logger"""

    normalized_level = log_level.upper()

    # Remove default handler
    logger.remove()

    # Add stderr handler
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=normalized_level,
        colorize=True,
    )

    # Add file handler
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=normalized_level,
        rotation="500 MB",
        retention="7 days",
    )