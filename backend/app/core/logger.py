# app/utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.config import settings

LOG_LEVEL = settings.LOG_LEVEL.upper()
LOG_FILE = settings.LOG_FILE

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Logger setup
logger = logging.getLogger("app_logger")
logger.setLevel(LOG_LEVEL)
logger.propagate = False

# Formatter
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s | %(name)s | %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Rotating File Handler
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
