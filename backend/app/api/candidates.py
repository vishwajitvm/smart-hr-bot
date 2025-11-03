# # app/api/candidates.py
# import logging
# from fastapi import APIRouter, HTTPException, BackgroundTasks
# from bson import ObjectId
# from pydantic import ValidationError
# from app.core.db import candidates_collection
# from app.models.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
# from app.utils.email_utils import send_email

# router = APIRouter()
# logger = logging.getLogger("candidates_api")


# def normalize_mongo_doc(doc: dict) -> dict:
#     """Convert MongoDB _id to string id and return safe dict."""
#     if not doc:
#         return {}
#     doc = {**doc}
#     doc["id"] = str(doc.pop("_id"))
#     return doc


# def send_thank_you_email(candidate_name: str, emails: list, background_tasks: BackgroundTasks):
#     """Send a professional thank-you email to the candidate."""
#     subject = "Thank You for Applying to Bee Logical"
#     body = f"""
#     <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
#         <h2 style="color: #004aad;">Thank You for Applying, {candidate_name}!</h2>
#         <p>We sincerely appreciate your interest in joining <strong>Bee Logical</strong>.</p>
#         <p>We have received your resume and application details successfully. Our recruitment team will carefully review your profile, and we will get in touch with you soon regarding the next steps.</p>
#         <p>In the meantime, feel free to visit our website: <a href="https://www.beelogical.com" target="_blank">www.beelogical.com</a></p>
#         <br>
#         <p>Best regards,<br>
#         <strong>Bee Logical Recruitment Team</strong></p>
#     </div>
#     """
#     for email in emails:
#         background_tasks.add_task(
#             send_email,
#             to_emails=[email],
#             subject=subject,
#             body=body
#         )


# Create
# app/api/candidates.py
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from bson import ObjectId
from pydantic import ValidationError
from app.core.db import candidates_collection
from app.models.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from app.utils.email_utils import send_email

router = APIRouter()
logger = logging.getLogger("candidates_api")


def normalize_mongo_doc(doc: dict) -> dict:
    """Convert MongoDB _id to string id and return safe dict."""
    if not doc:
        return {}
    doc = {**doc}
    doc["id"] = str(doc.pop("_id"))
    return doc


def send_thank_you_email(candidate_name: str, emails: list, background_tasks: BackgroundTasks):
    """Send a professional thank-you email to the candidate."""
    subject = "Thank You for Applying to Bee Logical"
    body = f"""
    <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #004aad;">Thank You for Applying, {candidate_name}!</h2>
        <p>We sincerely appreciate your interest in joining <strong>Bee Logical</strong>.</p>
        <p>We have received your resume and application details successfully. Our recruitment team will carefully review your profile, and we will get in touch with you soon regarding the next steps.</p>
        <p>In the meantime, feel free to visit our website: <a href="https://www.beelogical.com" target="_blank">www.beelogical.com</a></p>
        <br>
        <p>Best regards,<br>
        <strong>Bee Logical Recruitment Team</strong></p>
    </div>
    """
    for email in emails:
        background_tasks.add_task(
            send_email,
            to_emails=[email],
            subject=subject,
            body=body
        )


@router.post("/", response_model=CandidateResponse)
async def create_candidate(candidate: CandidateCreate, background_tasks: BackgroundTasks):
    try:
        # remove None values to avoid inserting junk
        doc = {k: v for k, v in candidate.model_dump().items() if v is not None}

        # Collect all emails
        all_emails = []
        if doc.get("email"):
            all_emails.append(doc["email"])
        if doc.get("other_emails") and isinstance(doc["other_emails"], list):
            all_emails.extend([e for e in doc["other_emails"] if e])
        all_emails = list(set(all_emails))  # remove duplicates

        logger.info(f"All candidate emails: {all_emails}")

        # always enforce defaults
        doc.update({"deleted": False, "status": "active"})

        # Insert candidate
        result = candidates_collection.insert_one(doc)
        saved = candidates_collection.find_one({"_id": result.inserted_id})
        candidate_response = CandidateResponse.model_validate(normalize_mongo_doc(saved))

        # Trigger Thank You email
        if all_emails:
            send_thank_you_email(candidate.name, all_emails, background_tasks)

        return candidate_response

    except ValidationError as ve:
        logger.exception("Validation error on create_candidate")
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception:
        logger.exception("Failed to insert candidate")
        raise HTTPException(status_code=500, detail="Failed to create candidate")


# Get all (exclude soft-deleted)
@router.get("/", response_model=list[CandidateResponse])
async def get_all_candidates():
    try:
        docs = candidates_collection.find({"deleted": False})
        return [CandidateResponse.model_validate(normalize_mongo_doc(d)) for d in docs]
    except Exception:
        logger.exception("Failed to fetch candidates")
        raise HTTPException(status_code=500, detail="Failed to fetch candidates")


# Get by id
@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate_by_id(candidate_id: str):
    try:
        d = candidates_collection.find_one({"_id": ObjectId(candidate_id), "deleted": False})
        if not d:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return CandidateResponse.model_validate(normalize_mongo_doc(d))
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Failed to fetch candidate {candidate_id}")
        raise HTTPException(status_code=500, detail="Failed to fetch candidate")


# Update
@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(candidate_id: str, updates: CandidateUpdate):
    try:
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        res = candidates_collection.update_one(
            {"_id": ObjectId(candidate_id), "deleted": False},
            {"$set": update_data},
        )
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")

        d = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
        return CandidateResponse.model_validate(normalize_mongo_doc(d))
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Failed to update candidate {candidate_id}")
        raise HTTPException(status_code=500, detail="Failed to update candidate")


# Soft delete
@router.delete("/{candidate_id}")
async def soft_delete_candidate(candidate_id: str):
    try:
        res = candidates_collection.update_one(
            {"_id": ObjectId(candidate_id)}, {"$set": {"deleted": True}}
        )
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return {"message": "Candidate soft deleted successfully"}
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Failed to soft delete candidate {candidate_id}")
        raise HTTPException(status_code=500, detail="Failed to delete candidate")


# Inactivate
@router.patch("/{candidate_id}/inactive")
async def inactivate_candidate(candidate_id: str):
    try:
        res = candidates_collection.update_one(
            {"_id": ObjectId(candidate_id), "deleted": False},
            {"$set": {"status": "inactive"}},
        )
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return {"message": "Candidate marked as inactive"}
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Failed to inactivate candidate {candidate_id}")
        raise HTTPException(status_code=500, detail="Failed to inactivate candidate")
