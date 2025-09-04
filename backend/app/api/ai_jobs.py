from fastapi import APIRouter, HTTPException
from app.models.job_ai import JobAIRequest, JobAIResponse, JobAISuggestion
from app.services.llm import generate_job_with_ai
from app.core.logger import get_logger
import time

router = APIRouter(prefix="/ai/jobs", tags=["AI Jobs"])
logger = get_logger(__name__)


# @router.post("/generate", response_model=JobAIResponse)
# async def generate_job_details(payload: JobAIRequest):
#     """
#     Generate job description, requirements, responsibilities, etc. using AI.
#     This does NOT persist to DB. Only logs the suggestion.
#     """
#     if not payload.title:
#         raise HTTPException(status_code=400, detail="Job title is required")

#     start_time = time.time()
#     try:
#         # Delegate to llm.py
#         suggestion: JobAISuggestion = await generate_job_with_ai(payload)
#         duration_ms = int((time.time() - start_time) * 1000)

#         logger.info({
#             "event": "ai_job_generated",
#             "title": payload.title,
#             "token": suggestion.token,
#             "duration_ms": duration_ms,
#         })

#         return JobAIResponse(
#             ok=True,
#             generated=suggestion,
#             model="gemini",  # updated: we are using Gemini model from llm.py
#             duration_ms=duration_ms,
#             cached=False,
#         )
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"❌ AI job generation failed: {e}")
#         raise HTTPException(status_code=500, detail="AI job generation failed")


@router.post("/generate", response_model=JobAIResponse)
async def generate_job_details(payload: JobAIRequest):
    """
    Generate job description, requirements, responsibilities, etc. using AI.
    This does NOT persist to DB. Only logs the suggestion.
    """
    if not payload.title:
        raise HTTPException(status_code=400, detail="Job title is required")

    start_time = time.time()
    try:
        # Delegate to llm.py
        suggestion: JobAISuggestion = await generate_job_with_ai(payload)
        duration_ms = int((time.time() - start_time) * 1000)

        # Build response (this has the token)
        response = JobAIResponse(
            ok=True,
            generated=suggestion,
            model="gemini",  # updated: we are using Gemini model from llm.py
            duration_ms=duration_ms,
            cached=False,
        )

        logger.info({
            "event": "ai_job_generated",
            "title": payload.title,
            "token": response.token,   # ✅ use token from response
            "duration_ms": duration_ms,
        })

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ AI job generation failed: {e}")
        raise HTTPException(status_code=500, detail="AI job generation failed")



