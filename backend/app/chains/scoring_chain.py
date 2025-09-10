# backend/app/chains/scoring_chain.py
from datetime import datetime
from typing import Dict, List
import json
import re
import logging

from app.models.scoring import CandidateScore, ScoringBreakdown, JobMatch, SentimentAnalysis
from app.chains.scoring_prompt import scoring_prompt_template
from app.services.llm import llm_service  # your Gemini service

logger = logging.getLogger(__name__)

def calculate_skill_score(candidate_skills: List[str], required_skills: List[str]) -> int:
    """
    Calculate skill match percentage
    """
    matched = len(set(candidate_skills) & set(required_skills))
    total = len(required_skills)
    return int((matched / total) * 100) if total > 0 else 0

async def extract_dynamic_scores(candidate_data: Dict, job_data: Dict, resume_text: str) -> Dict:
    """
    Generate dynamic scoring from Gemini LLM.
    """
    # Convert experience to integer safely
    years_of_experience = candidate_data.get("years_of_experience", 0)
    try:
        years_of_experience = int(years_of_experience)
    except (ValueError, TypeError):
        years_of_experience = 0

    prompt = scoring_prompt_template.format(
        skills=", ".join(candidate_data.get("skills", [])),
        experience=years_of_experience,
        resume_text=resume_text,
        job_description=job_data.get("description", "") if job_data else ""
    )

    try:
        response_text = await llm_service.generate_response(prompt)
        # Remove any ```json fences
        response_text = re.sub(r"^```[a-zA-Z]*\n?", "", response_text)
        response_text = response_text.rstrip("`").strip()

        # Extract JSON
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            response_text = match.group(0)

        data = json.loads(response_text)
        return data
    except Exception as e:
        logger.error(f"❌ Error parsing LLM response: {e}")
        raise

async def generate_candidate_score(candidate_data: Dict, job_data: Dict = None, resume_text: str = "") -> CandidateScore:
    """
    Generate full candidate scoring dynamically using Gemini LLM.
    """
    skills = candidate_data.get("skills", [])
    required_skills = job_data.get("skills", []) if job_data else []

    # Ensure years_of_experience is int
    years_of_experience = candidate_data.get("years_of_experience", 0)
    try:
        years_of_experience = int(years_of_experience)
    except (ValueError, TypeError):
        years_of_experience = 0

    # Dynamic LLM scores
    dynamic_scores = await extract_dynamic_scores(candidate_data, job_data, resume_text)

    scoring_breakdown = ScoringBreakdown(
        skills=calculate_skill_score(skills, required_skills),
        experience=min(100, int(years_of_experience / 5 * 100)),
        education=dynamic_scores.get("education", 0),
        projects=dynamic_scores.get("projects", 0),
        keywords=dynamic_scores.get("keywords", 0),
        ats=dynamic_scores.get("ats", 0),
        grammar=dynamic_scores.get("grammar", 0),
        soft_skills=dynamic_scores.get("soft_skills", 0),
        readability=dynamic_scores.get("readability", 0),
        cultural_fit=dynamic_scores.get("cultural_fit", 0),
        domain_relevance=dynamic_scores.get("domain_relevance", 0),
        certifications_score=dynamic_scores.get("certifications_score", 0)
    )

    job_match = JobMatch(
        skills_matched=list(set(skills) & set(required_skills)),
        skills_missing=list(set(required_skills) - set(skills)),
        keyword_density={
            "required_keywords": len(required_skills),
            "matched": len(set(skills) & set(required_skills)),
            "percentage": int(len(set(skills) & set(required_skills)) / len(required_skills) * 100)
            if required_skills else 0
        }
    ) if required_skills else None

    sentiment = SentimentAnalysis(
        overall="Positive",
        tone="Professional",
        soft_skills_extraction=dynamic_scores.get("soft_skills_extraction", [])
    )

    now = datetime.utcnow()
    return CandidateScore(
        candidate_id=str(candidate_data.get("id")),
        job_id=str(job_data.get("id")) if job_data else None,
        overall_score=scoring_breakdown.skills,
        fitment_score=int((scoring_breakdown.skills + scoring_breakdown.experience) / 2),
        scoring_breakdown=scoring_breakdown,
        job_match=job_match,
        sentiment=sentiment,
        strengths={
            "technical": list(set(skills) & set(required_skills))[:5],
            "soft": sentiment.soft_skills_extraction
        },
        weaknesses={
            "technical": list(set(required_skills) - set(skills))[:5],
            "soft": []  # can optionally extract missing soft skills from LLM
        },
        recommendation=dynamic_scores.get("recommendation", ""),
        fitment_status="Good Fit" if scoring_breakdown.skills > 70 else "Average",
        ranking_score=None,
        percentile=None,
        scoring_version="v1.1",
        deleted=False,
        deleted_at=None,
        created_at=now,
        updated_at=now
    )
