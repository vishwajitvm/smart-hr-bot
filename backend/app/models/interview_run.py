# app/models/interview_run.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class QuestionAnswerRecord(BaseModel):
    """
    Record saved per question during a run.
    Contains raw transcript URL + stt text + LLM evaluation fields.
    """
    qid: str
    question_text: str
    answer_audio_url: Optional[str] = None  # GridFS or external storage URL
    transcript_text: Optional[str] = None
    transcript_language: Optional[str] = None
    translated_text: Optional[str] = None
    stt_confidence: Optional[float] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    evaluation: Optional[Dict[str, Any]] = Field(default_factory=dict)  # LLM scoring breakdown per question


class InterviewRun(BaseModel):
    """
    A run is a concrete execution of an InterviewPlan.
    The run holds per-question recordings, transcripts and score artifacts.
    """
    run_id: str = Field(..., description="Unique run id (run_xxx)")
    interview_id: str = Field(..., description="Foreign key to InterviewPlan.interview_id")
    candidate_id: str = Field(..., description="Duplicate candidate id for quick queries")
    job_id: str = Field(..., description="Duplicate job id for quick queries")
    scheduled_at: Optional[datetime] = Field(None, description="When the run was scheduled to start (UTC)")
    started_at: Optional[datetime] = Field(None, description="Actual start time (UTC)")
    ended_at: Optional[datetime] = Field(None, description="End time (UTC)")
    status: str = Field("queued", description="queued | running | completed | failed | cancelled")
    twilio_call_sid: Optional[str] = Field(None, description="Call SID returned by Twilio")
    twilio_recording_url: Optional[str] = Field(None, description="Recording URL returned by Twilio (post-call)")
    question_answers: Optional[List[QuestionAnswerRecord]] = Field(default_factory=list, description="Per-question records")
    aggregate_score: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Final aggregated scoring summary")
    notifications_sent: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Notification audit entries (email/sms)")
    logs: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Operational logs specific to this run (structured)")
    error: Optional[str] = Field(None, description="Error message if run failed")
    created_at: datetime = Field(..., description="Run created timestamp")
    updated_at: datetime = Field(..., description="Run updated timestamp")
