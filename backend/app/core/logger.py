# app/utils/logger.py
from loguru import logger
import sys
import logging
from app.core.config import settings

def setup_logger():
    logger.remove()
    logger.add(
        settings.LOG_FILE if hasattr(settings, "LOG_FILE") else "logs/app.log",
        level=settings.LOG_LEVEL if hasattr(settings, "LOG_LEVEL") else "INFO",
        rotation="10 MB",
        retention="10 days",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    logger.add(sys.stdout, level="INFO")
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance with standard formatting.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
