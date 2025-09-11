from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ScoringBreakdown(BaseModel):
    skills: int
    experience: int
    education: int
    projects: int
    keywords: int
    ats: int
    grammar: int
    soft_skills: int
    readability: int
    cultural_fit: int
    domain_relevance: int
    certifications_score: int = 0

class JobMatch(BaseModel):
    skills_matched: List[str]
    skills_missing: List[str]
    keyword_density: Dict[str, int]  # {"required_keywords": 12, "matched": 9, "percentage": 75}

class SentimentAnalysis(BaseModel):
    overall: str
    tone: str
    soft_skills_extraction: List[str]

class CandidateScore(BaseModel):
    candidate_id: str
    job_id: Optional[str] = None
    overall_score: int
    fitment_score: int
    scoring_breakdown: ScoringBreakdown
    job_match: Optional[JobMatch] = None
    sentiment: Optional[SentimentAnalysis] = None
    strengths: Dict[str, List[str]]  # {"technical": [...], "soft": [...]}
    weaknesses: Dict[str, List[str]]  # {"technical": [...], "soft": [...]}
    recommendation: str
    fitment_status: str  # e.g., "Good Fit", "Average", "Poor"
    ranking_score: Optional[int] = None
    percentile: Optional[int] = None
    scoring_version: str
    deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
