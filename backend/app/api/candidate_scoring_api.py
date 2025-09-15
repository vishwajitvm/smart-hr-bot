# app/api/candidate_scoring_api.py

import logging
from logging.handlers import RotatingFileHandler
from fastapi import APIRouter, HTTPException, Body, Request
from bson import ObjectId
from datetime import datetime
from app.core.db import db
from app.models.scoring import CandidateScore
from app.models.candidate import CandidateResponse
from app.models.job import JobResponse
from app.chains.scoring_chain import generate_candidate_score

router = APIRouter(prefix="/candidate-scoring", tags=["Candidate Scoring"])

# -----------------------------
# Logging setup
# -----------------------------
logger = logging.getLogger("candidate_scoring_api")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    "logs/candidate_scoring.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - candidate_id=%(candidate_id)s - job_id=%(job_id)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def _safe_log_info(msg: str, candidate_id: str = "-", job_id: str = "-"):
    logger.info(msg, extra={"candidate_id": candidate_id, "job_id": job_id})


def _safe_log_warning(msg: str, candidate_id: str = "-", job_id: str = "-"):
    logger.warning(msg, extra={"candidate_id": candidate_id, "job_id": job_id})


def _safe_log_error(msg: str, candidate_id: str = "-", job_id: str = "-"):
    logger.error(msg, extra={"candidate_id": candidate_id, "job_id": job_id})


# -----------------------------
# API: Generate Candidate Score
# -----------------------------
@router.post("/generate-score")
async def generate_candidate_score_api(request: Request, payload: dict = Body(...)):
    client_host = request.client.host if request.client else "unknown"
    _candidate_id_for_log = "-"
    _job_id_for_log = "-"

    try:
        candidate_id = payload.get("candidate_id")
        if not candidate_id:
            _safe_log_warning("candidate_id not provided in payload")
            raise HTTPException(status_code=400, detail="candidate_id is required")

        # Fetch candidate
        query = {"_id": ObjectId(candidate_id)} if ObjectId.is_valid(candidate_id) else {"id": candidate_id}
        candidate = db["candidates"].find_one({**query, "deleted": False})
        if not candidate:
            _safe_log_warning(f"Candidate not found in DB - candidate_id={candidate_id}")
            raise HTTPException(status_code=404, detail="Candidate not found")

        candidate["id"] = str(candidate["_id"])
        candidate.pop("_id", None)
        _candidate_id_for_log = candidate["id"]
        _safe_log_info(f"Fetched candidate from DB - name={candidate.get('name')}", candidate_id=_candidate_id_for_log)

        # Fetch job using job_id from candidate
        job = None
        if candidate.get("job_id"):
            job_query = {"_id": ObjectId(candidate["job_id"])} if ObjectId.is_valid(str(candidate["job_id"])) else {"id": candidate["job_id"]}
            job = db["jobs"].find_one(job_query)
            if job:
                job["id"] = str(job["_id"])
                job.pop("_id", None)
                _job_id_for_log = job["id"]
                _safe_log_info(f"Fetched related job - title={job.get('title')}", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)
            else:
                _safe_log_warning(f"Job not found for candidate - job_id={candidate.get('job_id')}", candidate_id=_candidate_id_for_log)

        # Build resume_text dynamically
        resume_parts = []
        resume_parts.append(f"Candidate Name: {candidate.get('name', '')}")
        resume_parts.append(f"Email: {candidate.get('email', '')}")
        resume_parts.append(f"Phone: {candidate.get('phone', '')}")
        resume_parts.append(f"Location: {candidate.get('location', '')}")
        resume_parts.append(f"Years of Experience: {candidate.get('years_of_experience', '')}")
        resume_parts.append(f"Skills: {', '.join(candidate.get('skills', []))}")
        if job:
            resume_parts.append(f"Applying for Job: {job.get('title', '')}")
            resume_parts.append(f"Job Description: {job.get('description', '')}")
            resume_parts.append(f"Required Skills: {', '.join(job.get('skills', []))}")
        resume_text = "\n".join([p for p in resume_parts if p])

        # Candidate/Job objects
        try:
            candidate_obj = CandidateResponse(**candidate)
        except Exception as e:
            _safe_log_error(f"Error creating CandidateResponse object: {e}", candidate_id=_candidate_id_for_log)
            candidate_obj = None

        job_obj = None
        if job:
            try:
                job_obj = JobResponse(**job)
            except Exception as e:
                _safe_log_error(f"Error creating JobResponse object: {e}", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)
                job_obj = None

        # Generate score
        _safe_log_info(f"Generating dynamic score (client={client_host})", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)
        try:
            candidate_score: CandidateScore = await generate_candidate_score(
                candidate_data=(candidate_obj.model_dump() if candidate_obj else candidate),
                job_data=(job_obj.model_dump() if job_obj else (job or {})),
                resume_text=resume_text
            )
            _safe_log_info(f"Generated score - overall={candidate_score.overall_score}", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)
        except Exception as e:
            _safe_log_error(f"Error generating candidate score: {e}", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)
            raise HTTPException(status_code=500, detail=f"Error generating candidate score: {str(e)}")

        # Upsert candidate_score in DB
        query = {"candidate_id": candidate_score.candidate_id, "job_id": candidate_score.job_id}
        now = datetime.utcnow()
        doc = candidate_score.model_dump()
        doc["updated_at"] = now
        set_doc = doc.copy()
        # created_on_insert = {"created_at": doc.get("created_at", now)}
        created_on_insert = {"created_at": candidate_score.created_at}
        set_doc.pop("created_at", None)

        db["candidate_scores"].update_one(
            query,
            {"$set": set_doc, "$setOnInsert": created_on_insert},
            upsert=True
        )
        _safe_log_info("Stored/updated candidate score in DB", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)

        return {
            "candidates": [
                {
                    "candidate": CandidateResponse(**candidate).dict(),
                    "job": JobResponse(**job).dict() if job else None,
                    "resume_text": resume_text,
                    "score": candidate_score.model_dump()
                }
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        _safe_log_error(f"Unhandled error while generating score: {e}", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)
        raise HTTPException(status_code=500, detail=f"Unhandled error: {str(e)}")
