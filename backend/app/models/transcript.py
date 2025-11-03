# app/models/transcript.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class TranscriptSegment(BaseModel):
    """
    A small segment from STT result with timestamps and speaker label if available.
    """
    start_time: Optional[float] = Field(None, description="Segment start time in seconds")
    end_time: Optional[float] = Field(None, description="Segment end time in seconds")
    text: Optional[str] = Field(None, description="Segment transcript text")
    speaker: Optional[str] = Field(None, description="Speaker label (candidate | interviewer)")
    confidence: Optional[float] = Field(None, description="STT confidence 0..1")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TranscriptDoc(BaseModel):
    """
    Transcript document stored in transcripts_collection.
    This is the normalized per-run transcript.
    """
    transcript_id: str = Field(..., description="Unique transcript id (e.g. tx_...)")
    run_id: Optional[str] = Field(None, description="Related InterviewRun.run_id")
    interview_id: Optional[str] = Field(None, description="Related InterviewPlan.interview_id")
    candidate_id: Optional[str] = Field(None, description="Candidate id copy")
    job_id: Optional[str] = Field(None, description="Job id copy")
    audio_url: Optional[str] = Field(None, description="Location of audio (GridFS or external)")
    provider: Optional[str] = Field("assemblyai", description="STT provider used (assemblyai, whisper, deepgram)")
    language: Optional[str] = Field(None, description="Detected language code")
    full_text: Optional[str] = Field(None, description="Complete transcript text (plain)")
    segments: Optional[List[TranscriptSegment]] = Field(default_factory=list, description="Segmented transcript with timestamps")
    translation: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Translation info if any")
    stt_raw_response: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Raw STT provider response for audit")
    created_at: datetime = Field(..., description="When transcript was created")
    updated_at: datetime = Field(..., description="When transcript was last updated")
