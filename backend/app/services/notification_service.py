# app/services/notification_service.py

def send_email(to: str, subject: str, body: str) -> dict:
    # Stub for SMTP
    return {"status": "sent", "type": "email", "to": to, "subject": subject}

def send_sms(to: str, body: str) -> dict:
    # Stub for SMS provider
    return {"status": "sent", "type": "sms", "to": to, "message": body}
