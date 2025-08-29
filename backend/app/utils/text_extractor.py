import io
from pdfminer.high_level import extract_text
from docx import Document

def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """Extracts text from PDF or DOCX resumes"""
    if filename.lower().endswith(".pdf"):
        with io.BytesIO(file_bytes) as f:
            return extract_text(f)
    elif filename.lower().endswith(".docx"):
        with io.BytesIO(file_bytes) as f:
            doc = Document(f)
            return "\n".join([para.text for para in doc.paragraphs])
    else:
        return file_bytes.decode("utf-8", errors="ignore")
