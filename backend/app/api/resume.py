from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from bson import ObjectId
import gridfs
from app.core.db import db
import mimetypes
import io

router = APIRouter()

# GridFS instance (for file storage inside MongoDB)
fs = gridfs.GridFS(db)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Save file to Mongo GridFS
        file_id = fs.put(file.file, filename=file.filename, content_type=file.content_type)
        return {
            "message": "Resume uploaded successfully",
            "file_id": str(file_id),
            "download_url": f"/api/resume/{str(file_id)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}")
async def download_resume(file_id: str):
    try:
        file = fs.get(ObjectId(file_id))
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        # Detect MIME type (pdf, docx, etc.)
        mime_type, _ = mimetypes.guess_type(file.filename)
        mime_type = mime_type or "application/octet-stream"

        return StreamingResponse(
            io.BytesIO(file.read()),
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={file.filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
