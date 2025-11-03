# app/models/interview_question.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class InterviewQuestion(BaseModel):
    """
    Single question item used inside InterviewPlan.
    Keep this small and serializable.
    """
    qid: str = Field(..., description="Unique question id in the plan (e.g. q1, hr_1_xxx)")
    text: str = Field(..., description="Question text")
    type: str = Field(..., description="Type: technical | behavioral | scenario | hr_custom | intro | closing | followup")
    importance: int = Field(3, ge=1, le=5, description="Importance weight 1-5 (5 highest)")
    order: Optional[int] = Field(None, description="Planned order (1-based). Assigned by ordering function")
    auto_followup: Optional[bool] = Field(False, description="Whether to auto-generate or trigger a follow-up question based on answer quality")
    followup_template: Optional[str] = Field(None, description="Template text to generate follow-up (use placeholders like {answer})")
    expected_duration_seconds: Optional[int] = Field(None, description="Estimated time to ask+answer in seconds")
    tags: Optional[list[str]] = Field(default_factory=list, description="Arbitrary tags / topics (e.g. ['nodejs','performance'])")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Freeform metadata (e.g. provenance, heuristics)")
    created_at: Optional[datetime] = Field(None, description="When this question was created/added to plan")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
