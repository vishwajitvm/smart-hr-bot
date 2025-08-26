# app/api/auth.py

from fastapi import APIRouter, Depends
from app.models.auth import TokenResponse
from app.services.auth_service import login_with_google, login_with_keka, login_with_microsoft

router = APIRouter()

@router.get("/google", response_model=TokenResponse)
def google_login():
    return login_with_google()

@router.get("/keka", response_model=TokenResponse)
def keka_login():
    return login_with_keka()

@router.get("/microsoft", response_model=TokenResponse)
def microsoft_login():
    return login_with_microsoft()
