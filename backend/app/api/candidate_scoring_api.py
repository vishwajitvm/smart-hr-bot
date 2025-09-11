# backend/app/api/candidate_scoring_api.py
import logging
from logging.handlers import RotatingFileHandler
from fastapi import APIRouter, HTTPException, Body, Request
from bson import ObjectId
from datetime import datetime
import gridfs

from app.core.db import (
    candidates_collection,
    jobs_collection,
    db,
    candidate_scores_collection,
)
from app.models.scoring import CandidateScore
from app.models.candidate import CandidateResponse
from app.models.job import JobResponse
from app.chains.scoring_chain import generate_candidate_score

router = APIRouter(prefix="/candidate-scoring", tags=["Candidate Scoring"])

# GridFS setup for resumes
fs = gridfs.GridFS(db)

# Logging setup
logger = logging.getLogger("candidate_scoring_api")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    "logs/candidate_scoring.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


@router.post("/generate-score")
async def generate_candidate_score_api(request: Request, payload: dict = Body(...)):
    """
    Generate dynamic candidate score and store in DB.

    Request Body (JSON):
    {
        "candidate_id": "abc123"
    }

    Steps performed:
    1. Fetch candidate by ID (from candidates_collection).
    2. Fetch related job if candidate has a job_id.
    3. Fetch resume from GridFS if candidate has resume_id.
    4. Generate dynamic score using Gemini LLM.
    5. Store/update score in candidate_scores_collection.

    Returns:
    {
        "status": "success",
        "candidate": { ...candidate fields... },
        "job": { ...job fields... } | None,
        "resume": { "resume_id": "...", "filename": "...", "content_type": "..." } | None,
        "score": { ...scoring fields... }
    }
    """
    logger.info(f"Generate score request from {request.client.host} - Payload: {payload}")

    try:
        candidate_id = payload.get("candidate_id")
        if not candidate_id:
            logger.warning("candidate_id not provided in request")
            raise HTTPException(status_code=400, detail="candidate_id is required")

        # Candidate query
        query = {"_id": ObjectId(candidate_id)} if ObjectId.is_valid(candidate_id) else {"id": candidate_id}
        candidate = candidates_collection.find_one({**query, "deleted": False})
        if not candidate:
            logger.warning(f"Candidate not found: {candidate_id}")
            raise HTTPException(status_code=404, detail="Candidate not found")

        candidate["id"] = str(candidate["_id"])
        candidate.pop("_id", None)
        logger.info(f"Fetched candidate: {candidate['id']} - {candidate.get('name')}")

        # Related job
        job = None
        if candidate.get("job_id"):
            job_query = {"_id": ObjectId(candidate["job_id"])} if ObjectId.is_valid(str(candidate["job_id"])) else {"id": candidate["job_id"]}
            job = jobs_collection.find_one(job_query)
            if job:
                job["id"] = str(job["_id"])
                job.pop("_id", None)
                logger.info(f"Fetched related job: {job['id']} - {job.get('title')}")
            else:
                logger.warning(f"Job not found for candidate {candidate['id']} - Job ID: {candidate.get('job_id')}")

        # Related resume (fetch from GridFS)
        resume_text = ""
        resume_data = None
        if candidate.get("resume_id"):
            try:
                resume_file = fs.get(ObjectId(candidate["resume_id"]))
                resume_bytes = resume_file.read()
                try:
                    resume_text = resume_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    resume_text = ""  # fallback if binary cannot be decoded
                resume_data = {
                    "resume_id": str(candidate["resume_id"]),
                    "filename": resume_file.filename,
                    "content_type": resume_file.content_type
                }
                logger.info(f"Fetched resume {candidate['resume_id']} for candidate {candidate['id']}")
            except gridfs.errors.NoFile:
                logger.warning(f"Resume not found for candidate {candidate['id']} - Resume ID: {candidate.get('resume_id')}")

        # Prepare candidate and job objects for scoring
        candidate_obj = CandidateResponse(**candidate)
        job_obj = JobResponse(**job) if job else None

        # Generate dynamic score using Gemini LLM
        logger.info(f"Generating dynamic score for candidate {candidate_obj.id}")
        # candidate_score: CandidateScore = await generate_candidate_score(
        #     candidate=candidate_obj.dict(),
        #     job=job_obj.dict() if job_obj else None,
        #     resume_text=resume_text
        # )
        candidate_score: CandidateScore = await generate_candidate_score(
            candidate_data=candidate_obj.dict(),
            job_data=job_obj.dict() if job_obj else None,
            resume_text=resume_text
        )
        logger.info(f"Generated score for candidate {candidate_obj.id} - Overall Score: {candidate_score.overall_score}")

        # Store in candidate_scores collection
        candidate_scores_collection.update_one(
            {"candidate_id": candidate_score.candidate_id, "job_id": candidate_score.job_id},
            {"$set": candidate_score.dict()},
            upsert=True
        )
        logger.info(f"Stored candidate score in DB for candidate {candidate_obj.id}")

        return {
            "status": "success",
            "candidate": candidate_obj.dict(),
            "job": job_obj.dict() if job_obj else None,
            "resume": resume_data,
            "score": candidate_score.dict()
        }

    except Exception as e:
        logger.error(f"Error generating score: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating candidate score: {str(e)}")
