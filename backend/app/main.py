# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # allow all headers
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(llm.router, prefix="/api/llm", tags=["LLM"])

@app.get("/api/health")
def health():
    logger.info("Health check requested")
    return {"status": "ok"}

@app.get("/")
def root():
    logger.info("Root API called")
    return {"message": "Smart HR Bot API is running"}
