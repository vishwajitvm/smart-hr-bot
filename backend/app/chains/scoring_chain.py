# app/chains/scoring_chain.py

from datetime import datetime
from typing import Dict, List, Optional
import json
import logging
import uuid

from app.models.scoring import CandidateScore, ScoringBreakdown, JobMatch, SentimentAnalysis
from app.chains.scoring_prompt import scoring_prompt_template
from app.services.llm import llm_service, LLMServiceError

logger = logging.getLogger("scoring_chain")
logger.setLevel(logging.INFO)


# ------------------------------
# Deterministic helpers
# ------------------------------

def calculate_skill_score(candidate_skills: List[str], required_skills: List[str]) -> int:
    try:
        matched = len(set(map(str.lower, candidate_skills)) & set(map(str.lower, required_skills)))
        total = len(required_skills)
        return int((matched / total) * 100) if total > 0 else 0
    except Exception:
        return 0


def calculate_experience_score(years_of_experience: int, max_years: int = 5) -> int:
    try:
        years = int(years_of_experience)
    except Exception:
        years = 0
    score = int(min(100, (years / max_years) * 100))
    return max(0, score)


def calculate_keyword_density(resume_text: str, job_keywords: List[str]) -> Dict[str, int]:
    try:
        if not job_keywords:
            return {"required_keywords": 0, "matched": 0, "percentage": 0}
        resume_lower = (resume_text or "").lower()
        matched = sum(1 for kw in job_keywords if kw and kw.lower() in resume_lower)
        required = len(job_keywords)
        percentage = int((matched / required) * 100) if required > 0 else 0
        return {"required_keywords": required, "matched": matched, "percentage": percentage}
    except Exception:
        return {"required_keywords": 0, "matched": 0, "percentage": 0}


# Backwards compatibility helper (other modules may import)
def extract_first_json_object(text: str) -> dict:
    return llm_service.sanitize_json(text)


# ------------------------------
# LLM-assisted extraction
# ------------------------------

async def extract_dynamic_scores(candidate_data: Dict, job_data: Dict, resume_text: str) -> Dict:
    """
    Ask LLM for subjective pieces. Returns dict with keys:
    education, projects, ats, grammar, soft_skills, readability, cultural_fit, domain_relevance,
    certifications_score, sentiment, strengths, weaknesses, recommendation, additional_notes
    """
    # Precompute deterministic values to pass into prompt
    precomputed_skills_score = calculate_skill_score(candidate_data.get("skills", []), job_data.get("skills", []) if job_data else [])
    precomputed_experience_score = calculate_experience_score(candidate_data.get("years_of_experience", 0))
    precomputed_keyword_density = calculate_keyword_density(resume_text, job_data.get("keywords", []) if job_data else [])

    prompt = scoring_prompt_template.format(
        skills=", ".join(candidate_data.get("skills", []) or []),
        experience=precomputed_experience_score,
        resume_text=resume_text or "",
        job_description=(job_data.get("description") if job_data else "") or "",
        precomputed_skills_score=precomputed_skills_score,
        precomputed_experience_score=precomputed_experience_score,
        precomputed_keyword_density=json.dumps(precomputed_keyword_density)
    )

    try:
        raw = await llm_service.generate_response(prompt)
        logger.debug(f"[scoring_chain] LLM raw (truncated): {raw[:300]}")

        # Parse JSON from LLM response
        data = llm_service.sanitize_json(raw)

        # Ensure numeric fields are integers between 0 and 100; fallback 0
        numeric_keys = [
            "education", "projects", "ats", "grammar", "soft_skills",
            "readability", "cultural_fit", "domain_relevance", "certifications_score"
        ]
        for k in numeric_keys:
            if k in data:
                try:
                    data[k] = int(max(0, min(100, int(data[k]))))
                except Exception:
                    data[k] = 0
            else:
                data[k] = 0

        # Ensure nested/defaults
        data.setdefault("sentiment", {"overall": "Neutral", "tone": "Professional", "soft_skills_extraction": []})
        data.setdefault("strengths", {"technical": [], "soft": []})
        data.setdefault("weaknesses", {"technical": [], "soft": []})
        data.setdefault("recommendation", "")
        data.setdefault("additional_notes", "")

        return data

    except LLMServiceError as e:
        logger.warning(f"[scoring_chain] LLMService failed: {e}")
        return {}  # caller will handle fallback
    except Exception as e:
        logger.exception(f"[scoring_chain] Unexpected error extracting dynamic scores: {e}")
        return {}


# ------------------------------
# Main orchestration
# ------------------------------

async def generate_candidate_score(candidate_data: Dict, job_data: Optional[Dict] = None, resume_text: str = "") -> CandidateScore:
    """
    Returns CandidateScore (pydantic) combining deterministic and LLM-subjective parts.
    """
    request_id = str(uuid.uuid4())[:8]
    candidate_name = candidate_data.get("name") or candidate_data.get("candidate_name") or candidate_data.get("id")
    logger.info(f"[{request_id}] Starting scoring for candidate={candidate_name}")

    # Deterministic
    skills = candidate_data.get("skills", []) or []
    required_skills = job_data.get("skills", []) if job_data else []
    skills_score = calculate_skill_score(skills, required_skills)
    experience_score = calculate_experience_score(candidate_data.get("years_of_experience", 0))
    keyword_density = calculate_keyword_density(resume_text, job_data.get("keywords", []) if job_data else [])

    # LLM dynamic (may return {} on failure)
    dynamic = await extract_dynamic_scores(candidate_data, job_data or {}, resume_text)

    # Compose ScoringBreakdown
    scoring_breakdown = ScoringBreakdown(
        skills=skills_score,
        experience=experience_score,
        education=dynamic.get("education", 0),
        projects=dynamic.get("projects", 0),
        keywords=keyword_density.get("percentage", 0),
        ats=dynamic.get("ats", 0),
        grammar=dynamic.get("grammar", 0),
        soft_skills=dynamic.get("soft_skills", 0),
        readability=dynamic.get("readability", 0),
        cultural_fit=dynamic.get("cultural_fit", 0),
        domain_relevance=dynamic.get("domain_relevance", 0),
        certifications_score=dynamic.get("certifications_score", 0)
    )

    # Compute overall_score: hybrid weighting
    deterministic_component = int(round((scoring_breakdown.skills * 0.6) + (scoring_breakdown.experience * 0.3) + (scoring_breakdown.keywords * 0.1)))
    subjective_components = [
        scoring_breakdown.education,
        scoring_breakdown.projects,
        scoring_breakdown.ats,
        scoring_breakdown.grammar,
        scoring_breakdown.soft_skills,
        scoring_breakdown.readability,
        scoring_breakdown.cultural_fit,
        scoring_breakdown.domain_relevance
    ]
    subjective_component = int(round(sum(subjective_components) / len(subjective_components))) if any(subjective_components) else 0

    if subjective_component > 0:
        overall_score = int(round(deterministic_component * 0.65 + subjective_component * 0.35))
    else:
        overall_score = deterministic_component

    overall_score = max(0, min(100, overall_score))
    fitment_score = int(round((overall_score + scoring_breakdown.skills) / 2))

    # Fitment status (matches your prompt rules)
    if overall_score > 70:
        fitment_status = "Good Fit"
    elif 50 <= overall_score <= 70:
        fitment_status = "Average"
    else:
        fitment_status = "Poor"

    # JobMatch
    skills_matched = list(set(map(str.lower, skills)) & set(map(str.lower, required_skills))) if required_skills else []
    skills_missing = list(set(map(str.lower, required_skills)) - set(map(str.lower, skills))) if required_skills else []

    job_match = JobMatch(
        skills_matched=skills_matched,
        skills_missing=skills_missing,
        keyword_density={
            "required_keywords": keyword_density.get("required_keywords", 0),
            "matched": keyword_density.get("matched", 0),
            "percentage": keyword_density.get("percentage", 0)
        }
    ) if required_skills else None

    # Sentiment
    sentiment_payload = dynamic.get("sentiment", {"overall": "Neutral", "tone": "Professional", "soft_skills_extraction": []})
    sentiment = SentimentAnalysis(
        overall=sentiment_payload.get("overall", "Neutral"),
        tone=sentiment_payload.get("tone", "Professional"),
        soft_skills_extraction=sentiment_payload.get("soft_skills_extraction", [])
    )

    # Strengths & weaknesses
    strengths = {
        "technical": dynamic.get("strengths", {}).get("technical", skills_matched)[:5] if dynamic.get("strengths") else skills_matched[:5],
        "soft": dynamic.get("strengths", {}).get("soft", sentiment.soft_skills_extraction)[:5]
    }
    weaknesses = {
        "technical": dynamic.get("weaknesses", {}).get("technical", skills_missing)[:5],
        "soft": dynamic.get("weaknesses", {}).get("soft", [])[:5]
    }

    now = datetime.utcnow()

    candidate_score = CandidateScore(
        candidate_id=str(candidate_data.get("id") or candidate_data.get("_id") or ""),
        job_id=str(job_data.get("id")) if job_data and job_data.get("id") else None,
        overall_score=overall_score,
        fitment_score=fitment_score,
        scoring_breakdown=scoring_breakdown,
        job_match=job_match,
        sentiment=sentiment,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendation=(dynamic.get("recommendation") or "").strip(),
        fitment_status=fitment_status,
        ranking_score=None,
        percentile=None,
        scoring_version="v1.1",
        deleted=False,
        deleted_at=None,
        created_at=now,
        updated_at=now
    )

    logger.info(f"[{request_id}] Completed scoring: overall={overall_score}, fitment_status={fitment_status}")
    return candidate_score
