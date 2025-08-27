# app/utils/logger.py
from loguru import logger
import sys
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

