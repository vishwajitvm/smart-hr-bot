from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class JobBase(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    workMode: Optional[str] = "On-site"
    type: Optional[str] = "Full-time"
    experience: Optional[str] = "Entry"
    openings: int = 1
    salary: Optional[str] = None
    deadline: Optional[datetime] = None
    description: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    status: Optional[int] = 2  # 0 = Inactive, 1 = Active, 2 = Draft
    hiringManager: Optional[str] = None
    visibility: Optional[str] = "Public"
    # applicationMethod: Optional[str] = "Direct Apply"
    
    model: Optional[str] = None
    duration_ms: Optional[int] = None
    cached: Optional[bool] = None
    token: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobUpdate(JobBase):
    pass


class JobInDB(JobBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = False


class JobResponse(JobInDB):
    """Returned in API after DB insert/update"""
    pass
