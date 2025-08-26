# app/api/interview.py

from fastapi import APIRouter
from app.services.llm import run_interview

router = APIRouter()

@router.post("/simulate")
def simulate_interview(candidate_id: str):
    return run_interview(candidate_id)
