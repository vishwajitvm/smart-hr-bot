from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime


class JobAIRequest(BaseModel):
    title: str = Field(..., min_length=2, description="Job title to generate details for")
    locale: Optional[str] = Field("en", description="Language/locale preference")
    company_context: Optional[str] = Field(None, description="Optional company/team context")
    max_salary_suggestion: Optional[bool] = Field(True)


class JobAISuggestion(BaseModel):
    """Fields that AI is expected to generate (subset of full Job model)."""
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    workMode: Optional[str] = None
    type: Optional[str] = None
    experience: Optional[str] = None
    openings: Optional[int] = None
    salary: Optional[str] = None
    description: Optional[str] = None
    responsibilities: Optional[str] = None  # rich text HTML
    requirements: Optional[str] = None      # rich text HTML
    benefits: Optional[str] = None          # rich text HTML
    hiringManager: Optional[str] = None


class JobAIResponse(BaseModel):
    ok: bool
    generated: JobAISuggestion
    model: Optional[str] = None
    duration_ms: Optional[int] = None
    cached: bool = False
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique AI suggestion identifier")
