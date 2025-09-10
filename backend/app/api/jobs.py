# app/api/jobs.py
from fastapi import APIRouter, Body, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.job import JobCreate, JobUpdate, JobInDB, JobResponse
from app.core.db import jobs_collection

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)

# Helper to convert Mongo doc → Pydantic
def job_doc_to_response(doc) -> JobResponse:
    return JobResponse(
        id=str(doc["_id"]),
        title=doc["title"],
        department=doc.get("department"),
        location=doc.get("location"),
        workMode=doc.get("workMode"),
        type=doc.get("type"),
        experience=doc.get("experience"),
        openings=doc.get("openings", 1),
        salary=doc.get("salary"),
        deadline=doc.get("deadline"),
        description=doc.get("description"),
        responsibilities=doc.get("responsibilities"),
        requirements=doc.get("requirements"),
        benefits=doc.get("benefits"),
        status=doc.get("status", 2),
        hiringManager=doc.get("hiringManager"),
        visibility=doc.get("visibility", "Public"),
        applicationMethod=doc.get("applicationMethod", "Direct Apply"),
        created_at=doc.get("created_at"),
        updated_at=doc.get("updated_at"),
        is_deleted=doc.get("is_deleted", False),
    )

@router.get("/", response_model=List[JobResponse])
async def get_all_jobs():
    jobs = jobs_collection.find({"is_deleted": False})
    return [job_doc_to_response(j) for j in jobs]

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_by_id(job_id: str):
    job = jobs_collection.find_one({"_id": ObjectId(job_id), "is_deleted": False})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_doc_to_response(job)

@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(payload: JobCreate):
    new_job = payload.dict()
    new_job.update({
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_deleted": False,
    })
    result = jobs_collection.insert_one(new_job)
    job = jobs_collection.find_one({"_id": result.inserted_id})
    return job_doc_to_response(job)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: str, payload: JobUpdate):
    update_data = payload.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    result = jobs_collection.update_one(
        {"_id": ObjectId(job_id), "is_deleted": False},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_collection.find_one({"_id": ObjectId(job_id)})
    return job_doc_to_response(job)

@router.delete("/{job_id}", response_model=dict)
async def soft_delete_job(job_id: str):
    result = jobs_collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"message": f"Job {job_id} deleted successfully"}

@router.patch("/{job_id}/status", response_model=JobResponse)
async def update_job_status(job_id: str, status: int = Body(..., embed=True)):
    if status not in [0, 1]:
        raise HTTPException(status_code=400, detail="Invalid status value")

    result = jobs_collection.update_one(
        {"_id": ObjectId(job_id), "is_deleted": False},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_collection.find_one({"_id": ObjectId(job_id)})
    return job_doc_to_response(job)