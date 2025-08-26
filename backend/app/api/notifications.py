# app/api/notifications.py

from fastapi import APIRouter
from app.services.notification_service import send_email, send_sms

router = APIRouter()

@router.post("/email")
def email(to: str, subject: str, body: str):
    return send_email(to, subject, body)

@router.post("/sms")
def sms(to: str, body: str):
    return send_sms(to, body)
