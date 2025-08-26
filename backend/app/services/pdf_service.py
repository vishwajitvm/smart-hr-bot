# app/services/pdf_service.py

import fitz  # PyMuPDF
from app.chains.resume_chain import resume_chain

async def parse_resume(file) -> dict:
    content = ""
    with fitz.open(stream=await file.read(), filetype="pdf") as doc:
        for page in doc:
            content += page.get_text()

    return resume_chain(content)
