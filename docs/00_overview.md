# 📘 Smart HR Bot – Overview

## 🎯 Introduction
Smart HR Bot is an **AI-powered recruitment assistant** designed to help HR teams streamline and optimize the hiring process. By combining **AI-driven intelligence (LLMs)** with modern web technologies, Smart HR Bot automates repetitive tasks like resume parsing, candidate evaluation, interview simulation, scheduling, and notifications—freeing HR professionals to focus on decision-making rather than administration.

---

## 🚀 Vision
Traditional hiring is slow, manual, and biased. Our vision is to create a **co-pilot for recruiters** that:
- **Reduces hiring time** by automating resume screening and interview prep.
- **Improves candidate quality** through AI-driven evaluations and structured scoring.
- **Enhances collaboration** between HR, candidates, and hiring managers with shared dashboards and notifications.
- **Scales globally** with multi-language support and integrations with existing ATS systems.

---

## 🧩 Key Capabilities (Planned & Implemented)

- **Resume Parsing** → Upload resumes in PDF/DOCX formats and extract structured data (skills, education, work experience, achievements).
- **Candidate Evaluation** → AI-generated scores for skills, experience, and cultural fit.
- **Interview Simulation** → Adaptive interview questions, real-time analysis, and sentiment evaluation.
- **Voice Interview (Phase 2)** → AI-powered **first round voice-based interview** with real-time scoring based on answers and tone.
- **Screening Round (Phase 2/3)** → AI-driven **follow-up interview** for deeper evaluation and score generation.
- **Cheating Detection (Phase 3)** → Anti-cheating system using **OpenCV + YOLO (object detection)** and AI/ML to identify anomalies during online interviews.
- **Calendar Integration (Planned)** → Automated interview scheduling with Google Calendar.
- **Notifications (Planned)** → Email & SMS reminders via Twilio/Kaleyra.
- **Auth & Security** → Secure authentication using JWT & OAuth2 (Google, Microsoft, Keka SSO planned).
- **Analytics Dashboard** → HR insights, candidate statistics, and performance tracking.

---

## 🏗️ System at a Glance

Smart HR Bot consists of three major layers:

1. **Backend (FastAPI)**
   - REST APIs for resumes, interviews, scoring, jobs, and feedback.
   - Services for LLM integrations, vector storage, PDF parsing, and scheduling.
   - Celery + Redis for asynchronous tasks (resume parsing, evaluation jobs).
   - PostgreSQL + MongoDB hybrid database setup.

2. **Frontend (React + Vite + Tailwind)**
   - User-friendly HR dashboard.
   - Pages for resume library, interview simulations, calendar, job postings, and analytics.
   - API integration using Axios.

3. **AI Layer (LLMs + Chains)**
   - Resume Parser Chain.
   - Interview Simulation Chain.
   - Candidate Scoring Chain.
   - Feedback Generation Chain (planned).
   - Training Data Chain (future fine-tuning).

---

## 🗺️ Roadmap Snapshot

- **MVP (Phase 1)**: Resume upload, parsing, scoring, and basic dashboard.
- **Phase 2**: Voice-based interview round, AI-driven screening interviews, sentiment analysis.
- **Phase 3**: Cheating detection (OpenCV + YOLO + AI/ML), calendar integration, notifications, SSO integrations, advanced analytics.
- **Future Enhancements**: Multi-language support, deeper ATS integrations.

---

## ✨ Why Smart HR Bot?
- Cuts down **time-to-hire**.
- Reduces **manual workload** on HR teams.
- Provides **structured, unbiased insights** into candidate profiles.
- Introduces **voice and AI-driven interviews** for scalable hiring.
- Enhances fairness with **anti-cheating mechanisms**.
- Bridges the gap between **AI automation** and **human judgment**.

---

Smart HR Bot is more than just a tool—it’s a **next-generation recruitment assistant** that brings intelligence, automation, and efficiency into the hiring workflow.

