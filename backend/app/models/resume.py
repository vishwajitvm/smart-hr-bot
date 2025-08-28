from pydantic import BaseModel

class ResumeUploadResponse(BaseModel):
    message: str
    file_id: str
    download_url: str
