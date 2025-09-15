# app/models/scoring.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class ScoringBreakdown(BaseModel):
    skills: int = Field(..., ge=0, le=100)
    experience: int = Field(..., ge=0, le=100)
    education: int = Field(..., ge=0, le=100)
    projects: int = Field(..., ge=0, le=100)
    keywords: int = Field(..., ge=0, le=100)
    ats: int = Field(..., ge=0, le=100)
    grammar: int = Field(..., ge=0, le=100)
    soft_skills: int = Field(..., ge=0, le=100)
    readability: int = Field(..., ge=0, le=100)
    cultural_fit: int = Field(..., ge=0, le=100)
    domain_relevance: int = Field(..., ge=0, le=100)
    certifications_score: int = Field(0, ge=0, le=100)


class JobMatch(BaseModel):
    skills_matched: List[str] = []
    skills_missing: List[str] = []
    keyword_density: Dict[str, int] = Field(
        default_factory=lambda: {"required_keywords": 0, "matched": 0, "percentage": 0}
    )


class SentimentAnalysis(BaseModel):
    overall: str  # "Positive"/"Neutral"/"Negative"
    tone: str  # "Professional"/"Casual"/"Friendly"
    soft_skills_extraction: List[str] = []


class CandidateScore(BaseModel):
    candidate_id: str
    job_id: Optional[str] = None
    overall_score: int = Field(..., ge=0, le=100)
    fitment_score: int = Field(..., ge=0, le=100)
    scoring_breakdown: ScoringBreakdown
    job_match: Optional[JobMatch] = None
    sentiment: Optional[SentimentAnalysis] = None
    strengths: Dict[str, List[str]] = Field(default_factory=lambda: {"technical": [], "soft": []})
    weaknesses: Dict[str, List[str]] = Field(default_factory=lambda: {"technical": [], "soft": []})
    recommendation: str = ""
    fitment_status: str = ""  # e.g., "Good Fit", "Average", "Poor"
    ranking_score: Optional[int] = None
    percentile: Optional[int] = None
    scoring_version: str = "v1.1"
    deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
