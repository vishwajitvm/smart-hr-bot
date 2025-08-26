# app/main.py

from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import setup_logger
from app.api import auth, users, resume, interview, calendar, notifications, llm

# Setup logger
logger = setup_logger()

app = FastAPI(
    title="Smart HR Bot API",
    version="1.0.0",
    description="AI-powered Smart HR Bot backend"
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(resume.router, prefix="/resume", tags=["Resume"])
app.include_router(interview.router, prefix="/interview", tags=["Interview"])
app.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(llm.router, prefix="/llm", tags=["LLM"])


@app.get("/")
def root():
    logger.info("Root API called")
    return {"message": "Smart HR Bot API is running"}
