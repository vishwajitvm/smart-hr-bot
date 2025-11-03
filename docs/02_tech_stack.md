# 02_tech_stack.md

# 🛠️ Technology Stack

This document provides a detailed overview of the technologies used in the **Smart HR Bot** project, from backend to frontend, including infrastructure, AI/ML tools, and third-party integrations.

---

## 1️⃣ Backend

**Language & Framework:**
- **Python 3.11** → Core programming language.
- **FastAPI** → High-performance web framework for building REST APIs.

**Web Server & ASGI:**
- **Uvicorn** → ASGI server for running FastAPI apps.

**Database:**
- **MongoDB** → Primary database for storing users, candidates, resumes, chat logs, tokens, and scoring data.
- **Motor** → Async driver for MongoDB.

**ORM / Data Handling:**
- **Pydantic & Pydantic-Settings** → Data validation and environment settings management.

**Authentication & Security:**
- **python-jose[cryptography]** → JWT token management.
- **passlib[bcrypt]** → Password hashing.
- **cryptography (Fernet)** → Token encryption.
- **OAuth2 / SSO** → Google, Microsoft, Keka integrations.

**File Parsing & Resume Handling:**
- **PyMuPDF** → PDF parsing.
- **PyPDF2** → PDF manipulation.
- **docx2txt** → DOCX parsing.
- **python-docx** → DOCX reading/writing.
- **textract** → Fallback parser for DOC, RTF, ODT, TXT, PPTX.
- **pdfminer.six** → PDF text extraction.

**AI / LLM Integration:**
- **Google Gemini API (via google-generativeai)** → LLM for resume parsing, interview simulation, scoring, and job description generation.
- **LangChain** → Orchestration of LLM chains for parsing, evaluation, feedback, and scoring.
- **Pinecone** → Vector store for embedding-based similarity searches.

**HTTP & Requests:**
- **requests** → External HTTP requests.
- **python-multipart** → File uploads.

**Email & Notifications:**
- **google-api-python-client & google-auth** → Sending emails, calendar integration.
- **Twilio** → Voice interviews, SMS notifications.

**Testing:**
- **pytest** → Unit testing.
- **pytest-asyncio** → Async testing.
- **httpx** → HTTP requests testing.

**Logging & Utilities:**
- **loguru** → Application logging.
- **python-dateutil, dateparser** → Date handling.

**Containerization:**
- **Docker & Docker Compose** → Containerize backend and frontend for easy deployment.
- Base image: `python:3.11-slim`
- Exposes port 8000.

<!-- **Async Task Management:**
- **Celery + Redis** → Background tasks (future use: notifications, scoring, etc.). -->

---

## 2️⃣ Frontend

**Language & Framework:**
- **TypeScript** → Strongly typed JavaScript.
- **React 19.x** → Frontend framework.
- **Vite** → Frontend bundler and development server.

**UI & Styling:**
- **Bulma** → CSS framework for responsive UI.
- **react-bulma-components** → React components for Bulma.
- **TailwindCSS** → Utility-first CSS framework.
- **@fortawesome/fontawesome-free** → Icons.

**Routing:**
- **react-router-dom** → Client-side routing.

**Data Handling:**
- **axios** → HTTP client for API requests.
<!-- - **zustand** → State management. -->

**Charts & Visualization:**
- **recharts** → Charts and visual analytics.

**Text Editors:**
- **react-quill-new** → Rich text editor.

**Alerts & Notifications:**
- **sweetalert2** → Alert and popups.

**Icons & Utilities:**
- **react-icons** → Icon components.
- **react-is** → React utilities.

**Dev Tools & Linting:**
- **ESLint** + **eslint-plugin-react-hooks** + **eslint-plugin-react-refresh** → Linting & code quality.
- **TypeScript ESLint** → Type checking.
- **PostCSS & Autoprefixer** → CSS processing.

---

## 3️⃣ Infrastructure & Deployment

- **Docker & Docker Compose** → Backend and frontend containerization.
<!-- - **Nginx** → Reverse proxy (future production setup). -->
- **GitHub Actions** → CI/CD pipelines.

**Networking & Security:**
- CORS configured for frontend-backend communication.
- Environment variables managed through `.env`.

**Docker Example:**
- Backend runs on port 8000.
- Frontend runs on port 5173.
- Shared Docker network: `smart_hr_network`.

---

## 4️⃣ AI / ML & Features

- **Google Gemini LLM** → Resume parsing, interview Q&A, scoring.
- **OpenCV + YOLO** → Real-time cheating detection during video interviews.
- **AI Scoring Models** → Evaluation for skills, cultural fit, and behavioral analysis.
- **Twilio Voice + SMS** → First-round voice interview automation.

---

## 5️⃣ Summary

The stack is designed for **scalability, performance, and AI-driven automation**:
- Backend: FastAPI + Python + MongoDB + LLMs.
- Frontend: React + Vite + TypeScript + Bulma + Tailwind.
- AI / ML: Google Gemini, LangChain, OpenCV, YOLO.
- Notifications & Voice: Twilio + Google APIs.
- DevOps: Docker, Docker Compose, CI/CD.

This setup ensures modularity, maintainability, and easy extension for new AI-powered HR features.

