import logging
from logging.handlers import RotatingFileHandler
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Request
from typing import List
from bson import ObjectId
import gridfs
import io
import asyncio
import mimetypes

from app.core.db import db, candidates_collection
from app.services.resume_parser import ResumeParserService
from app.utils.text_extractor import extract_text_from_file
from app.utils.email_utils import send_email

# ------------------------------
# Router & GridFS Setup
# ------------------------------
router = APIRouter()
fs = gridfs.GridFS(db)
parser = ResumeParserService()

# ------------------------------
# Logger Setup
# ------------------------------
logger = logging.getLogger("bulk_resume_api")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    "logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# ------------------------------
# Helper: Send Thank You Email
# ------------------------------
def send_thank_you_email(candidate_name: str, emails: list, background_tasks: BackgroundTasks):
    subject = "Thank You for Applying to Bee Logical"
    body = f"""
    <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #004aad;">Thank You for Applying, {candidate_name}!</h2>
        <p>We sincerely appreciate your interest in joining <strong>Bee Logical</strong>.</p>
        <p>We have received your resume and application details successfully. Our recruitment team will carefully review your profile, and we will get in touch with you soon regarding the next steps.</p>
        <p>In the meantime, feel free to visit our website: <a href="https://www.beelogical.com" target="_blank">www.beelogical.com</a></p>
        <br>
        <p>Best regards,<br>
        <strong>Bee Logical Recruitment Team</strong></p>
    </div>
    """
    for email in emails:
        background_tasks.add_task(send_email, to_emails=[email], subject=subject, body=body)

# ------------------------------
# Bulk Upload Endpoint (accepts files, job_id, position)
# ------------------------------
@router.post("/bulk-upload")
async def bulk_upload_resumes(
    request: Request,
    background_tasks: BackgroundTasks = None
):
    logger.info(f"Received bulk upload request from {request.client.host}")

    # Parse multipart form manually
    form = await request.form()

    # Accept both "files" and "files[]"
    files = form.getlist("files") or form.getlist("files[]")

    # Extract additional fields
    job_id = form.get("job_id")
    position = form.get("position")

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    if len(files) > 15:
        raise HTTPException(status_code=400, detail="Maximum 15 files allowed per upload")

    results = []

    for file in files:
        try:
            # ------------------------------
            # Read and store file in GridFS
            # ------------------------------
            file_bytes = await file.read()
            file_id = fs.put(file_bytes, filename=file.filename, content_type=file.content_type)
            resume_url = f"/api/resume/{str(file_id)}"

            # ------------------------------
            # Extract text and parse
            # ------------------------------
            text = extract_text_from_file(file.filename, file_bytes)
            loop = asyncio.get_event_loop()
            parsed_data = await loop.run_in_executor(None, lambda: parser.parse_resume(text))

            # ------------------------------
            # Prepare candidate document
            # ------------------------------
            doc = {k: v for k, v in parsed_data.items() if v is not None}
            doc.update({
                "deleted": False,
                "status": "active",
                "resume_id": str(file_id),
                "resume_url": resume_url,
                "job_id": job_id,
                "position": position
            })

            # Collect all emails for thank-you
            all_emails = []
            if doc.get("email"):
                all_emails.append(doc["email"])
            if doc.get("other_emails") and isinstance(doc["other_emails"], list):
                all_emails.extend([e for e in doc["other_emails"] if e])
            all_emails = list(set(all_emails))

            # ------------------------------
            # Insert into MongoDB
            # ------------------------------
            result = candidates_collection.insert_one(doc)
            saved = candidates_collection.find_one({"_id": result.inserted_id})

            # ------------------------------
            # Append result
            # ------------------------------
            results.append({
                "file_name": file.filename,
                "status": "success",
                "candidate_id": str(saved["_id"]),
                "resume_id": str(file_id),
                "resume_url": resume_url,
                "job_id": job_id,
                "position": position
            })

        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}", exc_info=True)
            results.append({
                "file_name": file.filename,
                "status": "error",
                "error": str(e)
            })

    return {
        "message": f"{len(results)} file(s) processed successfully",
        "job_id": job_id,
        "position": position,
        "results": results
    }
