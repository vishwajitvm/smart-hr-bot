# app/models/interview.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class QuestionItem(BaseModel):
    qid: str
    text: str
    type: str  # technical | behavioral | scenario | hr_custom | intro | closing
    importance: int = Field(..., ge=1, le=5)
    order: Optional[int] = None
    auto_followup: Optional[bool] = False
    followup_template: Optional[str] = None
    metadata: Optional[dict] = {}


class InterviewPlan(BaseModel):
    interview_id: str
    candidate_id: str
    job_id: str
    questions: List[QuestionItem]
    created_by: str = "system"
    scheduled_at: Optional[datetime] = None
    status: str = "planned"  # planned, scheduled, running, completed, failed
    created_at: datetime
    updated_at: datetime
    extra: Optional[Any] = None


class InterviewRun(BaseModel):
    run_id: str
    interview_id: str
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    status: str = "queued"  # queued, running, completed, failed
    twilio_call_sid: Optional[str] = None
    recording_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
