# app/utils/email_utils.py
import smtplib
from typing import List, Optional, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.logger import get_logger
from app.utils.email_template import render_email_template
import time

logger = get_logger(__name__)


def send_email(
    to_emails: Union[str, List[str]],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    from_email: Optional[str] = None,
) -> dict:
    """
    Send an email using SMTP with a default HTML template.
    Supports multiple recipients, CC, and BCC.
    """
    start_time = time.time()
    try:
        logger.info("🔹 Starting email send process")

        # Normalize recipients
        if isinstance(to_emails, str):
            to_emails = [to_emails]
        all_recipients = to_emails + (cc or []) + (bcc or [])
        logger.info(f"Recipients: To={to_emails}, CC={cc}, BCC={bcc}")

        # Prepare email with template
        msg = MIMEMultipart()
        msg["From"] = from_email or settings.SMTP_USER
        msg["To"] = ", ".join(to_emails)
        if cc:
            msg["Cc"] = ", ".join(cc)
        msg["Subject"] = subject

        html_body = render_email_template(body, subject)
        msg.attach(MIMEText(html_body, "html"))
        logger.info("Email message constructed successfully")

        # Connect to SMTP
        logger.info(f"Connecting to SMTP server {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            logger.info("Starting TLS session")
            server.starttls()

            # Mask password length in logs
            logger.info(f"Logging in as {settings.SMTP_USER} "
                        f"(password length={len(settings.SMTP_PASSWORD)})")

            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            logger.info(f"Sending email to all recipients: {all_recipients}")
            server.sendmail(msg["From"], all_recipients, msg.as_string())

        duration_ms = int((time.time() - start_time) * 1000)
        logger.info({
            "event": "email_sent",
            "subject": subject,
            "to": to_emails,
            "cc": cc,
            "bcc": bcc,
            "duration_ms": duration_ms,
        })
        logger.info("✅ Email sent successfully")

        return {
            "status": "success",
            "message": f"Email sent to {to_emails}",
            "duration_ms": duration_ms,
        }

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error({
            "event": "email_failed",
            "error": str(e),
            "subject": subject,
            "to": to_emails,
            "duration_ms": duration_ms,
        })
        logger.error("❌ Email sending failed")
        return {
            "status": "error",
            "message": str(e),
            "duration_ms": duration_ms,
        }
