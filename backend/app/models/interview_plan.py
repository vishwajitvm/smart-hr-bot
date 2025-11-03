# app/models/interview_plan.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .interview_question import InterviewQuestion


class InterviewPlan(BaseModel):
    """
    Interview plan persisted in interviews_collection.
    This model represents the 'plan' — questions, scheduling meta, audit info.
    """
    interview_id: str = Field(..., description="Unique interview id (e.g. intvw_xxx)")
    candidate_id: str = Field(..., description="Reference to candidates collection (stringified ObjectId)")
    job_id: str = Field(..., description="Reference to jobs collection (stringified ObjectId)")
    title: Optional[str] = Field(None, description="Optional human readable title for the interview")
    questions: List[InterviewQuestion] = Field(default_factory=list, description="Ordered question plan")
    created_by: Optional[str] = Field("system", description="User or system who created this plan")
    scheduled_at: Optional[datetime] = Field(None, description="If scheduled, the planned datetime for the run (UTC)")
    calendar_event_id: Optional[str] = Field(None, description="Google Calendar / external planner event id")
    reminders: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Reminder schedule (email_12h, sms_15m etc.)")
    status: str = Field("planned", description="planned | scheduled | running | completed | cancelled | failed")
    consent_required: Optional[bool] = Field(True, description="Whether explicit audio consent is required from candidate")
    consent_recorded: Optional[bool] = Field(False, description="Whether consent was recorded")
    consent_timestamp: Optional[datetime] = Field(None, description="When consent was recorded (UTC)")
    question_version: Optional[str] = Field(None, description="LLM / prompt version used to generate questions")
    scoring_hint: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Hints for scoring service (weights, rubrics)")
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Freeform extension field for future data")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags to categorize interview - e.g. 'on-site','phone','junior'")
    node_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Runtime or orchestration metadata for workers")
