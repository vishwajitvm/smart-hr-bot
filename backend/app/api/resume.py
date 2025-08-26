# app/api/resume.py

from fastapi import APIRouter, UploadFile
from app.services.pdf_service import parse_resume

router = APIRouter()

@router.post("/parse")
async def parse(file: UploadFile):
    return await parse_resume(file)
