# app/api/candidate_scoring_api.py

import logging
from logging.handlers import RotatingFileHandler
from fastapi import APIRouter, HTTPException, Body, Request
from bson import ObjectId
from datetime import datetime
import gridfs
import tempfile
import os

from app.core.db import (
    candidates_collection,
    jobs_collection,
    db,
    candidate_scores_collection,
)
from app.models.scoring import CandidateScore
from app.models.candidate import CandidateResponse
from app.models.job import JobResponse
from app.chains.scoring_chain import generate_candidate_score, calculate_keyword_density

router = APIRouter(prefix="/candidate-scoring", tags=["Candidate Scoring"])

# GridFS setup
fs = gridfs.GridFS(db)

# Logging
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


@router.post("/generate-score")
async def generate_candidate_score_api(request: Request, payload: dict = Body(...)):
    client_host = request.client.host if request.client else "unknown"
    _candidate_id_for_log = "-"
    _job_id_for_log = "-"
    try:
        candidate_id = payload.get("candidate_id")
        if not candidate_id:
            logger.warning("candidate_id not provided in request")
            raise HTTPException(status_code=400, detail="candidate_id is required")

        # Query candidate (support ObjectId or custom id)
        query = {"_id": ObjectId(candidate_id)} if ObjectId.is_valid(candidate_id) else {"id": candidate_id}
        candidate = candidates_collection.find_one({**query, "deleted": False})
        if not candidate:
            logger.warning(f"Candidate not found: {candidate_id}")
            raise HTTPException(status_code=404, detail="Candidate not found")

        # normalize id
        candidate["id"] = str(candidate.get("_id") or candidate.get("id"))
        candidate.pop("_id", None)

        _candidate_id_for_log = candidate["id"]
        _safe_log_info(f"Fetched candidate from DB - name={candidate.get('name')}", candidate_id=_candidate_id_for_log)

        # Fetch job if present
        job = None
        if candidate.get("job_id"):
            job_query = {"_id": ObjectId(candidate["job_id"])} if ObjectId.is_valid(str(candidate["job_id"])) else {"id": candidate["job_id"]}
            job = jobs_collection.find_one(job_query)
            if job:
                job["id"] = str(job.get("_id") or job.get("id"))
                job.pop("_id", None)
                _job_id_for_log = job["id"]
                _safe_log_info(f"Fetched related job - title={job.get('title')}", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)
            else:
                logger.warning(f"Job not found for candidate {candidate['id']} - Job ID: {candidate.get('job_id')}", extra={"candidate_id": _candidate_id_for_log})

        # Fetch resume from GridFS and parse text
        resume_text = ""
        resume_data = None
        if candidate.get("resume_id"):
            try:
                resume_file = fs.get(ObjectId(candidate["resume_id"]))
                resume_bytes = resume_file.read()
                # Try as UTF-8 text first
                try:
                    resume_text = resume_bytes.decode("utf-8")
                except Exception:
                    # save to temp file and try pdf/docx extraction if libs present
                    tmp = tempfile.NamedTemporaryFile(delete=False)
                    tmp.write(resume_bytes)
                    tmp.close()
                    tmp_path = tmp.name
                    parsed = ""
                    try:
                        from pathlib import Path
                        suffix = Path(resume_file.filename or "").suffix.lower()
                        if suffix == ".pdf":
                            try:
                                import pdfplumber
                                with pdfplumber.open(tmp_path) as pdf:
                                    pages_text = [p.extract_text() or "" for p in pdf.pages]
                                    parsed = "\n".join(pages_text)
                            except Exception:
                                parsed = ""
                        elif suffix in [".doc", ".docx"]:
                            try:
                                import docx
                                doc = docx.Document(tmp_path)
                                parsed = "\n".join([p.text for p in doc.paragraphs])
                            except Exception:
                                parsed = ""
                    except Exception:
                        parsed = ""
                    resume_text = parsed or ""
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

                resume_data = {
                    "resume_id": str(candidate["resume_id"]),
                    "filename": getattr(resume_file, "filename", "unknown"),
                    "content_type": getattr(resume_file, "content_type", "unknown")
                }
                _safe_log_info("Fetched resume for candidate", candidate_id=_candidate_id_for_log)
            except gridfs.errors.NoFile:
                logger.warning(f"Resume not found for candidate {candidate['id']} - Resume ID: {candidate.get('resume_id')}", extra={"candidate_id": _candidate_id_for_log})

        # Candidate/Job response objects optional conversion
        try:
            candidate_obj = CandidateResponse(**candidate)
        except Exception:
            candidate_obj = None

        job_obj = None
        if job:
            try:
                job_obj = JobResponse(**job)
            except Exception:
                job_obj = None

        # Generate score
        _safe_log_info(f"Generating dynamic score (client={client_host})", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)
        try:
            candidate_score: CandidateScore = await generate_candidate_score(
                candidate_data=(candidate_obj.model_dump() if candidate_obj else candidate),
                job_data=(job_obj.model_dump() if job_obj else (job or {})),
                resume_text=resume_text or ""
            )
            _safe_log_info(f"Generated score - overall={candidate_score.overall_score}", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)
        except Exception as e:
            logger.exception("Error generating candidate score via chain", exc_info=True)
            # Surface a concise message to client, but preserve error in logs
            raise HTTPException(status_code=500, detail=f"Error generating candidate score: {str(e)}")

        # Upsert candidate_score into DB and preserve created_at
        query = {"candidate_id": candidate_score.candidate_id, "job_id": candidate_score.job_id}
        now = datetime.utcnow()
        doc = candidate_score.model_dump()  # pydantic v2 method
        # Ensure datetime objects are real datetimes if pydantic returned them as such
        doc["updated_at"] = now

        set_doc = doc.copy()
        created_on_insert = {"created_at": doc.get("created_at", now)}
        set_doc.pop("created_at", None)

        candidate_scores_collection.update_one(
            query,
            {
                "$set": set_doc,
                "$setOnInsert": created_on_insert
            },
            upsert=True
        )

        _safe_log_info("Stored/updated candidate score in DB", candidate_id=_candidate_id_for_log, job_id=_job_id_for_log)

        return {
            "status": "success",
            "candidate": candidate,
            "job": job,
            "resume": resume_data,
            "score": candidate_score.model_dump()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unhandled error while generating score: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unhandled error: {str(e)}")
