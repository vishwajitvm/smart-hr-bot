from fastapi import APIRouter, HTTPException
from fastapi.params import Body
from app.core.db import db
from app.models.candidate import CandidateResponse
from app.models.job import JobResponse
from app.models.scoring import CandidateScore
from pydantic import BaseModel
from bson import ObjectId

router = APIRouter(prefix="/candidates-listing-with-score", tags=["Candidates"])


# Request model for pagination
class CandidateListRequest(BaseModel):
    page: int = 1
    limit: int = 10


@router.post("/list")
async def list_candidates(payload: CandidateListRequest):
    """
    Fetch paginated candidate list with related job, resume, and score details.
    Accepts JSON body:
    {
        "page": 1,
        "limit": 10
    }
    """

    page = payload.page
    limit = payload.limit
    skip = (page - 1) * limit

    # total candidates count
    total_count = db["candidates"].count_documents({"deleted": False})

    # fetch candidates with pagination
    candidates_cursor = (
        db["candidates"]
        .find({"deleted": False})
        .sort("_id", -1)
        .skip(skip)
        .limit(limit)
    )
    candidates = list(candidates_cursor)

    result = []

    for candidate in candidates:
        # Convert Mongo `_id` → string `id`
        candidate["id"] = str(candidate["_id"])
        candidate.pop("_id", None)

        # fetch related job
        job = None
        if candidate.get("job_id"):
            query = (
                {"_id": ObjectId(candidate["job_id"])}
                if ObjectId.is_valid(str(candidate["job_id"]))
                else {"id": candidate["job_id"]}
            )
            job = db["jobs"].find_one(query)
            if job:
                job["id"] = str(job["_id"])
                job.pop("_id", None)

        # fetch related resume
        resume = None
        if candidate.get("resume_id"):
            query = (
                {"_id": ObjectId(candidate["resume_id"])}
                if ObjectId.is_valid(str(candidate["resume_id"]))
                else {"id": candidate["resume_id"]}
            )
            resume = db["resumes"].find_one(query)
            if resume:
                resume["id"] = str(resume["_id"])
                resume.pop("_id", None)

        # fetch related candidate score
        score = None
        score_doc = db["candidate_scores"].find_one({"candidate_id": candidate["id"], "deleted": False})
        if score_doc:
            score_doc["id"] = str(score_doc["_id"])
            score_doc.pop("_id", None)
            try:
                score = CandidateScore(**score_doc).dict()
            except Exception:
                score = score_doc  # fallback raw dict if validation fails

        result.append({
            "candidate": CandidateResponse(**candidate).dict(),
            "job": JobResponse(**job).dict() if job else None,
            "resume": resume if resume else None,
            "score": score
        })

    # pagination info
    total_pages = (total_count + limit - 1) // limit  # ceil division
    has_more = page < total_pages

    return {
        "candidates": result,
        "pagination": {
            "totalCount": total_count,
            "totalPages": total_pages,
            "currentPage": page,
            "hasMore": has_more,
        }
    }


@router.post("/get-candidate-by-id")
async def get_candidate_by_id(payload: dict = Body(...)):
    """
    Fetch a single candidate by ID (POST) with related job, resume, and score details.
    Request Body:
    {
        "candidate_id": "abc123"
    }
    """

    candidate_id = payload.get("candidate_id")
    if not candidate_id:
        raise HTTPException(status_code=400, detail="candidate_id is required")

    # Candidate query
    query = (
        {"_id": ObjectId(candidate_id)}
        if ObjectId.is_valid(candidate_id)
        else {"id": candidate_id}
    )

    candidate = db["candidates"].find_one({**query, "deleted": False})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate["id"] = str(candidate["_id"])
    candidate.pop("_id", None)

    # Related job
    job = None
    if candidate.get("job_id"):
        job_query = (
            {"_id": ObjectId(candidate["job_id"])}
            if ObjectId.is_valid(str(candidate["job_id"]))
            else {"id": candidate["job_id"]}
        )
        job = db["jobs"].find_one(job_query)
        if job:
            job["id"] = str(job["_id"])
            job.pop("_id", None)

    # Related resume
    resume = None
    if candidate.get("resume_id"):
        resume_query = (
            {"_id": ObjectId(candidate["resume_id"])}
            if ObjectId.is_valid(str(candidate["resume_id"]))
            else {"id": candidate["resume_id"]}
        )
        resume = db["resumes"].find_one(resume_query)
        if resume:
            resume["id"] = str(resume["_id"])
            resume.pop("_id", None)

    # Related candidate score
    score = None
    score_doc = db["candidate_scores"].find_one({"candidate_id": candidate["id"], "deleted": False})
    if score_doc:
        score_doc["id"] = str(score_doc["_id"])
        score_doc.pop("_id", None)
        try:
            score = CandidateScore(**score_doc).dict()
        except Exception:
            score = score_doc

    # Same response structure as list API
    return {
        "candidates": [
            {
                "candidate": CandidateResponse(**candidate).dict(),
                "job": JobResponse(**job).dict() if job else None,
                "resume": resume if resume else None,
                "score": score
            }
        ]
    }
