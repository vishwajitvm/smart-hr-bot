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
│   │   ├── main.py                # FastAPI entrypoint (uvicorn app.main:app --reload)
│   │   │
│   │   ├── api/                   # Routers (controllers)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Google, Keka, MS SSO routes
│   │   │   ├── users.py           # User CRUD APIs
│   │   │   ├── resume.py          # Resume parsing APIs
│   │   │   ├── interview.py       # AI interview simulation endpoints
│   │   │   ├── calendar.py        # Google Calendar integration
│   │   │   ├── notifications.py   # Email/SMS notifications
│   │   │
│   │   ├── chains/ (or workflows/) # AI pipelines
│   │   │   ├── __init__.py
│   │   │   ├── resume_parser.py   # LLM + PDF parsing
│   │   │   ├── interview_chain.py # Simulated interview flow
│   │   │   ├── evaluation.py      # Sentiment/score evaluation
│   │   │
│   │   ├── services/              # Business logic + integrations
│   │   │   ├── __init__.py
│   │   │   ├── vectorstore.py     # FAISS / Pinecone storage
│   │   │   ├── llm.py             # Gemini / OpenAI client wrappers
│   │   │   ├── pdf_service.py     # Resume PDF extraction
│   │   │   ├── calendar_service.py# Google Calendar API wrapper
│   │   │   ├── notification_service.py # Email, Twilio/Kaleyra SMS
│   │   │   ├── auth_service.py    # OAuth2, JWT utils
│   │   │
│   │   ├── models/                # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── interview.py
│   │   │   ├── auth.py
│   │   │
│   │   ├── core/                  # Infra & configs
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Env settings
│   │   │   ├── logger.py          # Logging setup
│   │   │   ├── security.py        # Password rules, JWT
│   │   │   ├── db.py              # Mongo/Postgres init
│   │   │
│   │   ├── utils/                 # Helper functions
│   │   │   ├── __init__.py
│   │   │   ├── file_utils.py
│   │   │   ├── text_utils.py
│   │   │   ├── date_utils.py
│   │   │
│   │   └── logs/
│   │       └── app.log
│   │
│   ├── tests/                     # Unit + integration tests
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_resume.py
│   │   ├── test_interview.py
│   │
│   ├── requirements.txt           # Python deps
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .env.example               # Env vars template
│   └── alembic/        # if using DB migrations
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── InterviewUI.jsx
│   │   │   ├── ResumeUpload.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Interviews.jsx
│   │   │   ├── Calendar.jsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.js             # Axios wrapper
│   │   │   ├── auth.js            # Auth calls
│   │   │   ├── resume.js          # Resume parsing calls
│   │   │   ├── interview.js       # Interview simulation calls
│   │   │
│   │   ├── App.jsx
│   │   ├── index.jsx
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── docs/
│   ├── architecture.md
│   ├── api_reference.md
│   └── roadmap.md
│
├── scripts/
│   ├── seed_data.py
│   ├── backup_db.py
│
├── .gitignore
├── README.md
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

### Backend
```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker (Full stack)
```bash
docker-compose up --build
```

---

## 📄 License

MIT License. Free to use & modify.  
