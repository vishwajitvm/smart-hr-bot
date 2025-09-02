import logging
from logging.handlers import RotatingFileHandler
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
from bson import ObjectId
import gridfs
from app.core.db import db
import mimetypes
import io
import asyncio
from app.services.resume_parser import ResumeParserService
from app.utils.text_extractor import extract_text_from_file  # ✅ add util

# Router & GridFS
router = APIRouter()
fs = gridfs.GridFS(db)
parser = ResumeParserService()

# Logging setup
logger = logging.getLogger("resume_api")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    "logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


@router.post("/upload")
async def upload_resume(request: Request, file: UploadFile = File(...)):
    logger.info(f"Received resume upload from {request.client.host}")
    try:
        # Read file content once
        file_bytes = await file.read()

        # Store in GridFS
        file_id = fs.put(file_bytes, filename=file.filename, content_type=file.content_type)
        logger.info(f"Stored file in GridFS: {file_id}")

        # ✅ Extract text from uploaded file
        text = extract_text_from_file(file.filename, file_bytes)

        # Run parsing in background thread
        loop = asyncio.get_event_loop()
        parsed_data = await loop.run_in_executor(None, lambda: parser.parse_resume(text))

        response = {
            "message": "Resume uploaded & parsed successfully",
            "file_id": str(file_id),
            "download_url": f"/api/resume/{str(file_id)}",
            "resume_id": str(file_id),
            "resume_url": f"/api/resume/{str(file_id)}",
            **parsed_data
        }
        logger.info(f"Upload success response: {response}")
        return response
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@router.get("/{file_id}")
async def download_resume(request: Request, file_id: str):
    logger.info(f"Download request for file {file_id} from {request.client.host}")
    try:
        file = fs.get(ObjectId(file_id))
        if not file:
            logger.warning(f"File not found: {file_id}")
            raise HTTPException(status_code=404, detail="File not found")

        mime_type, _ = mimetypes.guess_type(file.filename)
        mime_type = mime_type or "application/octet-stream"

        logger.info(f"Serving file {file.filename}")
        return StreamingResponse(
            io.BytesIO(file.read()),
            media_type=mime_type,
            headers={"Content-Disposition": f"attachment; filename={file.filename}"}
        )
    except Exception as e:
        logger.error(f"Download error {file_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
