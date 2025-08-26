# app/api/calendar.py

from fastapi import APIRouter
from app.services.calendar_service import schedule_meeting

router = APIRouter()

@router.post("/schedule")
def schedule(candidate_email: str):
    return schedule_meeting(candidate_email)
