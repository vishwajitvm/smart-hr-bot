# app/api/notifications.py

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from app.utils.email_utils import send_email
from app.services.notification_service import send_sms

router = APIRouter()


# ------------------------------
# Pydantic Models
# ------------------------------

class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    from_email: Optional[EmailStr] = None


class SMSRequest(BaseModel):
    to: str
    body: str


# ------------------------------
# Email Endpoint
# ------------------------------

@router.post("/email")
def send_email_route(request: EmailRequest, background_tasks: BackgroundTasks):
    """
    Send an email asynchronously using BackgroundTasks.
    Returns immediately while email is sent in background.
    """
    background_tasks.add_task(
        send_email,
        to_emails=request.to,
        subject=request.subject,
        body=request.body,
        cc=request.cc,
        bcc=request.bcc,
        from_email=request.from_email
    )
    return {"status": "success", "message": "Email is being sent in the background"}


# ------------------------------
# SMS Endpoint
# ------------------------------

@router.post("/sms")
def send_sms_route(request: SMSRequest):
    """
    Send SMS using the notification service.
    """
    try:
        result = send_sms(request.to, request.body)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS sending failed: {str(e)}")


# ------------------------------
# Test Email Endpoint
# ------------------------------

@router.post("/send-test-email")
def send_test_email(background_tasks: BackgroundTasks):
    """
    Sends a test email to verify SMTP configuration.
    """
    test_email = "wolverinevm001@gmail.com"
    background_tasks.add_task(
        send_email,
        to_emails=[test_email],
        subject="Smart HR Bot Test Email",
        body="<h3>This is a test email from Smart HR Bot 🚀</h3>"
    )
    return {"status": "success", "message": f"Test email is being sent to {test_email}"}
