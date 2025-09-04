from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from app.models.job import JobCreate, JobUpdate, JobResponse, JobInDB
from app.core.logger import get_logger

# In-memory DB (replace with MongoDB/Postgres)
DB: dict[str, JobInDB] = {}

router = APIRouter(prefix="/jobs", tags=["Jobs"])
logger = get_logger(__name__)


@router.post("", response_model=JobResponse)
async def create_job(payload: JobCreate):
    """Create a new job posting and persist in DB."""
    job = JobInDB(**payload.dict())
    DB[job.id] = job
    logger.info({"event": "job_created", "job_id": job.id})
    return job


@router.get("", response_model=List[JobResponse])
async def list_jobs(show_deleted: bool = False):
    """List all jobs, filter out deleted by default."""
    jobs = [job for job in DB.values() if show_deleted or not job.is_deleted]
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Fetch a single job by ID."""
    job = DB.get(job_id)
    if not job or job.is_deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: str, payload: JobUpdate):
    """Update a job posting."""
    job = DB.get(job_id)
    if not job or job.is_deleted:
        raise HTTPException(status_code=404, detail="Job not found")

    updated = job.copy(update=payload.dict(exclude_unset=True))
    updated.updated_at = datetime.utcnow()
    DB[job_id] = updated
    logger.info({"event": "job_updated", "job_id": job_id})
    return updated


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Soft delete a job posting."""
    job = DB.get(job_id)
    if not job or job.is_deleted:
        raise HTTPException(status_code=404, detail="Job not found")

    job.is_deleted = True
    job.updated_at = datetime.utcnow()
    DB[job_id] = job
    logger.info({"event": "job_deleted", "job_id": job_id})
    return {"ok": True, "message": "Job soft deleted"}
