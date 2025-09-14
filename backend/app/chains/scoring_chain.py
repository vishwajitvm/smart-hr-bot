# app/chains/scoring_chain.py

import json
import logging
import uuid
from typing import Dict, Optional
from datetime import datetime

from app.models.scoring import CandidateScore, ScoringBreakdown, SentimentAnalysis
from app.chains.scoring_prompt import scoring_prompt_template
from app.services.llm import llm_service

logger = logging.getLogger("scoring_chain")
logger.setLevel(logging.INFO)

# ------------------------------
# LLM-assisted extraction
# ------------------------------
async def extract_scores(candidate_data: Dict, job_data: Dict, resume_text: str) -> Dict:
    prompt = scoring_prompt_template.format(
        candidate_name=candidate_data.get("name", ""),
        skills=", ".join(candidate_data.get("skills", []) or []),
        experience=str(candidate_data.get("years_of_experience", 0)),
        resume_text=resume_text or "",
        job_description=(job_data.get("description") if job_data else "") or ""
    )

    logger.info("===== LLM Scoring Prompt =====")
    logger.info(f"Candidate: {candidate_data.get('name')}")
    logger.info(f"Job: {job_data.get('title') if job_data else 'N/A'}")
    logger.info(prompt[:2000])  # truncate for logs
    logger.info("===== END PROMPT =====")

    try:
        raw = await llm_service.generate_response(prompt)
        logger.info("===== LLM Raw Response =====")
        logger.info(raw[:2000])
        logger.info("===== END LLM Raw Response =====")

        data = llm_service.sanitize_json(raw)

        # Normalize numeric fields
        numeric_keys = [
            "overall_score", "fitment_score", "education", "projects", "skills", "experience",
            "keywords", "ats", "grammar", "soft_skills", "readability",
            "cultural_fit", "domain_relevance", "certifications_score"
        ]
        for k in numeric_keys:
            try:
                data[k] = int(data.get(k, 0))
                data[k] = max(0, min(100, data[k]))
            except Exception:
                data[k] = 0

        # Ensure defaults
        data.setdefault("sentiment", {"overall": "Neutral", "tone": "Professional", "soft_skills_extraction": []})
        data.setdefault("strengths", {"technical": [], "soft": []})
        data.setdefault("weaknesses", {"technical": [], "soft": []})
        data.setdefault("recommendation", "")
        data.setdefault("fitment_status", "Poor")
        data.setdefault("additional_notes", "")

        return data

    except Exception as e:
        logger.exception(f"[extract_scores] Error: {e}")
        return {}

# ------------------------------
# Main orchestration
# ------------------------------
async def generate_candidate_score(candidate_data: Dict, job_data: Optional[Dict] = None, resume_text: str = "") -> CandidateScore:
    request_id = str(uuid.uuid4())[:8]
    candidate_name = candidate_data.get("name", "Unknown")
    logger.info(f"[{request_id}] Starting scoring for candidate={candidate_name}")

    dynamic = await extract_scores(candidate_data, job_data or {}, resume_text)

    breakdown = ScoringBreakdown(
        skills=dynamic.get("skills", 0),
        experience=dynamic.get("experience", 0),
        education=dynamic.get("education", 0),
        projects=dynamic.get("projects", 0),
        keywords=dynamic.get("keywords", 0),
        ats=dynamic.get("ats", 0),
        grammar=dynamic.get("grammar", 0),
        soft_skills=dynamic.get("soft_skills", 0),
        readability=dynamic.get("readability", 0),
        cultural_fit=dynamic.get("cultural_fit", 0),
        domain_relevance=dynamic.get("domain_relevance", 0),
        certifications_score=dynamic.get("certifications_score", 0),
    )

    now = datetime.utcnow()

    score = CandidateScore(
        candidate_id=candidate_data.get("id"),
        job_id=job_data.get("id") if job_data else None,
        overall_score=dynamic.get("overall_score", 0),
        fitment_score=dynamic.get("fitment_score", 0),
        scoring_breakdown=breakdown,
        job_match=None,
        sentiment=SentimentAnalysis(**dynamic.get("sentiment")) if dynamic.get("sentiment") else None,
        strengths=dynamic.get("strengths", {}),
        weaknesses=dynamic.get("weaknesses", {}),
        recommendation=dynamic.get("recommendation", ""),
        fitment_status=dynamic.get("fitment_status", "Poor"),
        ranking_score=None,
        percentile=None,
        scoring_version="v2.0",
        created_at=now,   # ✅ REQUIRED FIELD FIX
        updated_at=now    # ✅ REQUIRED FIELD FIX
    )

    logger.info(f"[{request_id}] Finished scoring for candidate={candidate_name}")
    return score
