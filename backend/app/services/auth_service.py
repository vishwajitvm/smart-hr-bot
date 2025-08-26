# app/services/auth_service.py

from app.models.auth import TokenResponse
from app.core.config import settings

def login_with_google() -> TokenResponse:
    return TokenResponse(
        access_token=settings.GOOGLE_TOKEN,
        token_type="bearer"
    )

def login_with_keka() -> TokenResponse:
    return TokenResponse(
        access_token=settings.KEKA_TOKEN,
        token_type="bearer"
    )

def login_with_microsoft() -> TokenResponse:
    return TokenResponse(
        access_token=settings.MICROSOFT_TOKEN,
        token_type="bearer"
    )
