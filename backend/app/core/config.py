# app/core/config.py
import os
# from pydantic import BaseSettings
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # ========================
    # Application
    # ========================
    APP_NAME: str = "Smart HR Bot"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    # ========================
    # Logging
    # ========================
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "logs/app.log"

    # ========================
    # Database
    # ========================
    MONGO_URI: str
    MONGO_DB_NAME: str
    ASTRA_DB_API_KEY: str = None  # optional Cassandra/Astra

    # ========================
    # Security / JWT
    # ========================
    ENCRYPTION_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # ========================
    # OAuth / SSO
    # ========================
    GOOGLE_CLIENT_ID: str = None
    GOOGLE_CLIENT_SECRET: str = None
    KEKA_CLIENT_ID: str = None
    KEKA_CLIENT_SECRET: str = None
    MS_CLIENT_ID: str = None
    MS_CLIENT_SECRET: str = None
    
    # ========================
    # GEMINI (LLM)
    # ========================
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash"   # default, can override via .env
    VECTORSTORE_PATH: str = "./vectorstore"
    EMBEDDING_MODEL_NAME: str = "gemini-embedding-001"
    VECTOR_DIM: int = 768

    # ========================
    # Email / Notifications
    # ========================
    SMTP_HOST: str = None
    SMTP_PORT: int = 587
    SMTP_USER: str = None
    SMTP_PASSWORD: str = None

    # ========================
    # Rate Limiting
    # ========================
    RATE_LIMIT_MAX: int = 25
    RATE_LIMIT_WINDOW: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
