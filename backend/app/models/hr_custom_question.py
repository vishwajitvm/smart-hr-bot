# app/models/hr_custom_question.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class HRCustomQuestionItem(BaseModel):
    """
    Individual HR provided question item; can be stored per candidate or per job.
    Allows HR to supply 'importance' and follow-up rules.
    """
    qid: Optional[str] = Field(None, description="Optional HR supplied id (if they want)")
    text: str = Field(..., description="Question text")
    importance: int = Field(3, ge=1, le=5, description="HR provided importance")
    auto_followup: Optional[bool] = Field(False, description="Whether follow-up should be auto triggered")
    followup_template: Optional[str] = Field(None, description="Template to generate follow-up")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Extra meta")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class HRCustomQuestionsDoc(BaseModel):
    """
    Document stored in hr_custom_questions_collection.
    Either candidate_id or job_id must be present to scope questions.
    """
    doc_id: Optional[str] = Field(None, description="Internal document id (string)")
    candidate_id: Optional[str] = Field(None, description="If set, questions for a particular candidate")
    job_id: Optional[str] = Field(None, description="If set, questions for a particular job")
    custom_questions: List[HRCustomQuestionItem] = Field(default_factory=list)
    created_by: Optional[str] = Field("hr_user", description="Creator user id or system")
    active: bool = Field(True, description="Whether this doc is active")
    notes: Optional[str] = Field(None, description="Optional notes about these custom questions")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
