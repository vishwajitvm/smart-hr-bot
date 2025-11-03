from fastapi import APIRouter, HTTPException, Path, BackgroundTasks
from fastapi.params import Body
from app.core.db import db
from app.models.candidate import CandidateResponse
from app.core.db import candidate_chats_collection
from app.models.candidate_chat import CandidateChatModel
from app.chains.candidate_chat_chain import run_candidate_chat
from app.models.job import JobResponse
from app.models.scoring import CandidateScore
from pydantic import BaseModel
from bson import ObjectId
import logging
from pymongo import DESCENDING
from datetime import datetime
from app.utils.email_utils import send_email
from dateutil.parser import parse


router = APIRouter(prefix="/candidates-listing-with-score", tags=["Candidates"])
logger = logging.getLogger(__name__)

class ApprovedCandidateListRequest(BaseModel):
    """Pagination request model for approved candidates listing."""
    page: int = 1
    limit: int = 10
    

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
    
@router.post("/chat")
async def candidate_chat(payload: dict):
    """
    Handles candidate chat:
    - Accepts nested payloads from frontend
    - Extracts candidate_id and job_id
    - Runs AI analysis
    - Saves chat log in Mongo
    """
    try:
        logger.info("▶️ /api/candidates/chat called")
        logger.debug("📥 Raw Payload: %s", payload)

        # Single candidate payload
        if "candidate" in payload:
            candidates = [payload["candidate"]]
        # Multiple candidates
        elif "candidates" in payload:
            candidates = payload["candidates"]
        else:
            raise HTTPException(status_code=400, detail="No candidate data provided")

        question = payload.get("question")
        enriched_candidates = []

        for entry in candidates:
            candidate_obj = entry.get("candidate", entry)
            if "candidate" in candidate_obj:  # flatten if nested
                candidate_obj = candidate_obj["candidate"]

            job_obj = entry.get("job", {})

            candidate_id = candidate_obj.get("id") or candidate_obj.get("candidate_id")
            job_id = job_obj.get("id") or candidate_obj.get("job_id") or entry.get("job_id")

            if not candidate_id or not job_id:
                logger.error("❌ Missing candidate_id or job_id in payload: %s", entry)
                raise HTTPException(status_code=400, detail="candidate_id and job_id are required")

            logger.info("🔎 Processing candidate_id=%s job_id=%s", candidate_id, job_id)

            # Run AI chain
            ai_response = await run_candidate_chat(
                {"candidate": candidate_obj, "job": job_obj},
                question
            )

            # Save chat log
            chat_log = CandidateChatModel(
                candidate_id=str(candidate_id),
                job_id=str(job_id),
                question=question,
                response=ai_response,
                meta={
                    "score": entry.get("score"),
                    "source": "candidate_chat_api"
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            candidate_chats_collection.insert_one(chat_log.model_dump(by_alias=True))
            logger.info("✅ Chat log inserted into candidate_chats_collection")

            enriched_candidates.append({
                "candidate": candidate_obj,
                "job": job_obj,
                "score": entry.get("score", {}),
                "ai_chat": ai_response
            })

        logger.info("🎯 Returning enriched candidates with AI insights")
        return {"candidates": enriched_candidates}

    except Exception as e:
        logger.exception("💥 Error in /api/candidates/chat")
        raise HTTPException(status_code=500, detail=str(e))


def send_candidate_approval_email(candidate, background_tasks: BackgroundTasks):
    """Schedule an approval email to be sent in the background."""
    subject = f"Application Approved - {candidate.get('position', 'Your Application')}"
    body = f"""
        <p>Dear {candidate.get('name', 'Candidate')},</p>
        <p>We are pleased to inform you that your application for the position of 
        <strong>{candidate.get('position', 'the applied role')}</strong> has been <b>approved</b> for the next stage of our hiring process.</p>
        <p>Our team will reach out to you soon with further details.</p>
        <p>Best Regards,<br><strong>Bee Logical HR Team</strong></p>
    """
    background_tasks.add_task(
        send_email,
        to_emails=[candidate["email"]],
        subject=subject,
        body=body
    )


def send_candidate_rejection_email(candidate, background_tasks: BackgroundTasks):
    """Schedule a rejection email to be sent in the background."""
    subject = f"Application Update - {candidate.get('position', 'Your Application')}"
    body = f"""
        <p>Dear {candidate.get('name', 'Candidate')},</p>
        <p>Thank you for your interest in the <strong>{candidate.get('position', 'applied role')}</strong> position.</p>
        <p>After careful consideration, we regret to inform you that we will not be moving forward with your application at this time.</p>
        <p>We appreciate the time you took to apply and wish you the best in your future endeavors.</p>
        <p>Kind regards,<br><strong>Bee Logical HR Team</strong></p>
    """
    background_tasks.add_task(
        send_email,
        to_emails=[candidate["email"]],
        subject=subject,
        body=body
    )


@router.post("/{candidate_id}/approve")
async def approve_candidate(
    candidate_id: str = Path(..., description="Candidate ID"),
    background_tasks: BackgroundTasks = None
):
    try:
        logger.info("✅ Approving candidate: %s", candidate_id)

        query = (
            {"_id": ObjectId(candidate_id)}
            if ObjectId.is_valid(candidate_id)
            else {"id": candidate_id}
        )

        candidate_doc = db["candidates"].find_one({**query, "deleted": False})
        if not candidate_doc:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Update candidate
        update_result = db["candidates"].update_one(
            query,
            {"$set": {"stage_resume_review_status": 1, "updated_at": datetime.utcnow()}}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No update performed")

        candidate_doc["id"] = str(candidate_doc["_id"])
        candidate_doc.pop("_id", None)
        candidate = CandidateResponse(**candidate_doc)

        # Schedule background email
        if candidate.email:
            send_candidate_approval_email(candidate.dict(), background_tasks)

        logger.info("🎯 Candidate %s approved successfully", candidate_id)
        return {"status": "success", "message": "Candidate approved successfully", "candidate_id": candidate_id}

    except Exception as e:
        logger.exception("💥 Error approving candidate")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/{candidate_id}/reject")
async def reject_candidate(
    candidate_id: str = Path(..., description="Candidate ID"),
    background_tasks: BackgroundTasks = None
):
    try:
        logger.info("🚫 Rejecting candidate: %s", candidate_id)

        query = (
            {"_id": ObjectId(candidate_id)}
            if ObjectId.is_valid(candidate_id)
            else {"id": candidate_id}
        )

        candidate_doc = db["candidates"].find_one({**query, "deleted": False})
        if not candidate_doc:
            raise HTTPException(status_code=404, detail="Candidate not found")

        update_result = db["candidates"].update_one(
            query,
            {"$set": {"stage_resume_review_status": 2, "updated_at": datetime.utcnow()}}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No update performed")

        candidate_doc["id"] = str(candidate_doc["_id"])
        candidate_doc.pop("_id", None)
        candidate = CandidateResponse(**candidate_doc)

        # Schedule background email
        if candidate.email:
            send_candidate_rejection_email(candidate.dict(), background_tasks)

        logger.info("🛑 Candidate %s rejected successfully", candidate_id)
        return {"status": "success", "message": "Candidate rejected successfully", "candidate_id": candidate_id}

    except Exception as e:
        logger.exception("💥 Error rejecting candidate")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/approved-candidates-list")
async def list_approved_candidates(payload: ApprovedCandidateListRequest):
    """
    Fetch paginated list of approved candidates:
    - stage_ai_voice_call_status: 0 or 1
    - stage_resume_review_status: 1
    - job.deadline >= current UTC datetime
    """
    try:
        page = max(payload.page, 1)
        limit = max(payload.limit, 1)
        skip = (page - 1) * limit
        now = datetime.utcnow()

        logger.info(f"Fetching approved candidates — page={page}, limit={limit}, now={now}")

        # --- Step 1: Filter candidates ---
        candidate_filter = {
            "deleted": False,
            "stage_resume_review_status": 1,
            "$or": [
                {"stage_ai_voice_call_status": {"$exists": False}},
                {"stage_ai_voice_call_status": {"$ne": 1}}
            ]
        }

        total_count = db["candidates"].count_documents(candidate_filter)
        logger.info(f"Total matching candidates: {total_count}")

        # --- Step 2: Fetch candidates with pagination ---
        candidates_cursor = db["candidates"].find(candidate_filter).sort("_id", -1).skip(skip).limit(limit)
        candidates_list = list(candidates_cursor)
        
        # print("Fetched candidates:", candidates_list)

        final_result = []

        for candidate in candidates_list:
            candidate_id = str(candidate.pop("_id"))
            candidate["id"] = candidate_id

            # --- Step 3: Fetch job and check deadline ---
            job_data = None
            job_id = candidate.get("job_id")
            if job_id:
                try:
                    job_query = {"_id": ObjectId(job_id)} if ObjectId.is_valid(str(job_id)) else {"id": job_id}
                    job_doc = db["jobs"].find_one(job_query)
                    if job_doc:
                        job_deadline = job_doc.get("deadline")
                        # Convert string to datetime if needed
                        if isinstance(job_deadline, str):
                            job_deadline = parse(job_deadline)
                        if job_deadline and job_deadline < now:
                            logger.info(f"Skipping candidate {candidate_id} — job expired")
                            continue
                        job_doc["id"] = str(job_doc.pop("_id"))
                        job_data = JobResponse(**job_doc).dict()
                except Exception as e:
                    logger.error(f"Error fetching job for candidate {candidate_id}: {e}")
                    continue

            # --- Step 4: Fetch resume ---
            resume_data = None
            resume_id = candidate.get("resume_id")
            if resume_id:
                try:
                    resume_query = {"_id": ObjectId(resume_id)} if ObjectId.is_valid(str(resume_id)) else {"id": resume_id}
                    resume_doc = db["resumes"].find_one(resume_query)
                    if resume_doc:
                        resume_doc["id"] = str(resume_doc.pop("_id"))
                        resume_data = resume_doc
                except Exception as e:
                    logger.error(f"Error fetching resume for candidate {candidate_id}: {e}")

            # --- Step 5: Fetch candidate score ---
            score_data = None
            try:
                score_doc = db["candidate_scores"].find_one({"candidate_id": candidate_id, "deleted": False})
                if score_doc:
                    score_doc["id"] = str(score_doc.pop("_id"))
                    try:
                        score_data = CandidateScore(**score_doc).dict()
                    except Exception:
                        score_data = score_doc
            except Exception as e:
                logger.error(f"Error fetching score for candidate {candidate_id}: {e}")

            # --- Step 6: Append to result ---
            final_result.append({
                "candidate": CandidateResponse(**candidate).dict(),
                "job": job_data,
                "resume": resume_data,
                "score": score_data
            })

        total_pages = (total_count + limit - 1) // limit
        has_more = page < total_pages

        return {
            "candidates": final_result,
            "pagination": {
                "totalCount": total_count,
                "totalPages": total_pages,
                "currentPage": page,
                "hasMore": has_more,
            }
        }

    except Exception as e:
        logger.exception("💥 Error fetching approved candidates")
        raise HTTPException(status_code=500, detail=str(e))
    
    
