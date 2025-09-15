# 🤖 Smart HR Bot

Smart HR Bot is an **AI-powered recruitment assistant** that helps HR teams streamline the hiring process.  
It leverages **FastAPI (backend)**, **React (frontend)**, and **LLMs (Google Gemini / OpenAI)** to parse resumes, simulate interviews, evaluate candidates, and automate scheduling + notifications.

---

## 📂 Project Structure

```bash
smart-hr-bot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── resume.py
│   │   │   ├── interview.py
│   │   │   ├── calendar.py
│   │   │   ├── notifications.py
│   │   │   ├── feedback.py
│   │   │   ├── scoring.py
│   │   │   └── jobs.py
│   │   │
│   │   ├── chains/
│   │   │   ├── __init__.py
│   │   │   ├── resume_parser.py
│   │   │   ├── interview_chain.py
│   │   │   ├── evaluation.py
│   │   │   ├── scoring_chain.py
│   │   │   ├── feedback_chain.py
│   │   │   └── training_data_chain.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── vectorstore.py
│   │   │   ├── llm.py
│   │   │   ├── pdf_service.py
│   │   │   ├── calendar_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── scoring_service.py
│   │   │   ├── interview_service.py
│   │   │   └── feedback_service.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── interview.py
│   │   │   ├── auth.py
│   │   │   ├── feedback.py
│   │   │   ├── scoring.py
│   │   │   └── job.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── logger.py
│   │   │   ├── security.py
│   │   │   └── db.py
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── file_utils.py
│   │   │   ├── text_utils.py
│   │   │   ├── date_utils.py
│   │   │   ├── email_utils.py
│   │   │   ├── validation_utils.py
│   │   │   └── logging_utils.py
│   │   │
│   │   └── logs/
│   │       └── app.log
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_resume.py
│   │   ├── test_interview.py
│   │   ├── test_calendar.py
│   │   ├── test_feedback.py
│   │   ├── test_scoring.py
│   │   └── test_jobs.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .env.example
│   └── alembic/
│       ├── env.py
│       ├── README
│       └── versions/
│           └── (migration scripts)
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── InterviewUI.tsx
│   │   │   ├── ResumeUpload.tsx
│   │   │   ├── DashboardCard.tsx
│   │   │   ├── CalendarWidget.tsx
│   │   │   └── css/
│   │   │       ├── Navbar.css
│   │   │       ├── Sidebar.css
│   │   │       ├── ResumeUpload.css
│   │   │       ├── DashboardCard.css
│   │   │       └── CalendarWidget.css
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Interviews.tsx
│   │   │   ├── Calendar.tsx
│   │   │   ├── ResumeLibrary.tsx
│   │   │   ├── Feedback.tsx
│   │   │   └── JobPostings.tsx
│   │   │
│   │   ├── services/
│   │   │   └── api.ts
│   │   │
│   │   ├── utils/
│   │   │   ├── dateUtils.ts
│   │   │   ├── textUtils.ts
│   │   │   └── fileUtils.ts
│   │   │
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   ├── vite-env.d.ts
│   │   └── main.css
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── docs/
│   ├── architecture.md
│   ├── api_reference.md
│   ├── roadmap.md
│   └── changelog.md
│
├── scripts/
│   ├── seed_data.py
│   ├── backup_db.py
│   └── cleanup_temp_files.py
│
├── .gitignore
└── README.md
```

---

## 🚀 Features

- **Resume Parsing** → Extracts and analyzes resumes using AI (LLM + embeddings).  
- **Candidate Evaluation** → Scores candidates on skills, experience, and cultural fit.  
- **Interview Simulation** → AI-powered interview questions + sentiment analysis.  
- **Calendar Integration** → Auto-schedules interviews via Google Calendar.  
- **Notifications** → Email + SMS (Twilio / Kaleyra) reminders.  
- **Auth & Security** → JWT, OAuth2 (Google, Microsoft, Keka SSO).  
- **Analytics Dashboard** → HR insights on candidate performance.  

---

## 🛠️ Tech Stack

**Backend**
- FastAPI  
- Pydantic  
- FAISS / Pinecone  
- PostgreSQL / MongoDB  
- Google Gemini / OpenAI API  
- Celery + Redis (for async tasks)  

**Frontend**
- React + Vite  
- Tailwind CSS  
- Axios  
- React Router  

**Infra**
- Docker, Docker Compose  
- Nginx (reverse proxy)  
- GitHub Actions (CI/CD)  

---

## 📌 Development Plan

1. **MVP**  
   - Resume upload & parsing  
   - Candidate evaluation  
   - Basic dashboard  

2. **Phase 2**  
   - Interview simulation (AI Q&A)  
   - Sentiment analysis  
   - Google Calendar integration  

3. **Phase 3**  
   - Notifications (Email/SMS)  
   - Full SSO integration  
   - Analytics dashboard  

4. **Future Enhancements**  
   - Multi-language support  
   - Voice interview simulation  
   - Integration with ATS (Greenhouse, Lever, etc.)  

---

## ⚡ Setup Instructions

## ⚙️ Backend Setup (FastAPI)

### 1️⃣ Create virtual environment
```bash
cd backend
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate    # (Windows)
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run server
```bash
uvicorn app.main:app --reload
```

API runs at: **http://localhost:8000**

Docs: **http://localhost:8000/docs**

---

## 🎨 Frontend Setup (React + Vite + TypeScript)

### 1️⃣ Install dependencies
```bash
cd frontend
npm install
```

### 2️⃣ Run dev server
```bash
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 🐳 Docker Setup

Run both frontend + backend using Docker Compose:

```bash
docker-compose up --build
```

---

