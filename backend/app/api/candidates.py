# app/api/candidates.py
import logging
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from pydantic import ValidationError
from app.core.db import candidates_collection
from app.models.candidate import CandidateCreate, CandidateUpdate, CandidateResponse

router = APIRouter()
logger = logging.getLogger("candidates_api")


def normalize_mongo_doc(doc: dict) -> dict:
    """Convert MongoDB _id to string id and return safe dict."""
    if not doc:
        return {}
    doc = {**doc}
    doc["id"] = str(doc.pop("_id"))
    return doc


# Create
@router.post("/", response_model=CandidateResponse)
async def create_candidate(candidate: CandidateCreate):
    try:
        # remove None values to avoid inserting junk
        doc = {k: v for k, v in candidate.model_dump().items() if v is not None}

        # always enforce defaults
        doc.update({"deleted": False, "status": "active"})

        result = candidates_collection.insert_one(doc)
        saved = candidates_collection.find_one({"_id": result.inserted_id})

        return CandidateResponse.model_validate(normalize_mongo_doc(saved))
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
