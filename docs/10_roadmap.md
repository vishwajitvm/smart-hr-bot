# 10_roadmap.md

# Smart HR Bot - Roadmap

This document provides a detailed roadmap for the Smart HR Bot project, outlining completed features, current implementations, and planned future enhancements. It serves as a reference for developers, testers, and stakeholders to understand the chronological sequence of development and upcoming priorities.

---

## 1. Overview

The Smart HR Bot is an AI-powered recruitment assistant designed to streamline candidate screening, scoring, and interview processes. It integrates AI/ML features, resume parsing, automated scoring, and interactive chat-based assessments. The roadmap below categorizes work by completed, ongoing, and planned future features.

---

## 2. Completed Features (Phase 1)

### 2.1 Backend / API
- Resume parsing and text extraction, stored in MongoDB.
- Candidate CRUD operations:
  - Submit, fetch, update, delete, and inactivate candidates.
- Job CRUD operations:
  - Create, fetch, update, delete jobs.
  - AI-generated job descriptions based on title input.
- Candidate scoring APIs based on resume and job applied.
- AI chat integration for selected candidate resume data.
- Health check and system health endpoints.

### 2.2 Frontend / UI
- Basic dashboard with charts and visualizations of candidate scores.
- Editable resume submission forms.
- Interactive AI chat interface for candidate assessment.
- Candidate listing and scoring visualizations.

### 2.3 Candidate scoring algorithm Integration
- Candidate scoring algorithm based on skills, experience, education, projects, ATS, grammar, soft skills, readability, cultural fit, domain relevance, certifications.
- AI chat using candidate resume data.

---

## 3. Current Implementations (Phase 2)

### 3.1 Candidate Metrics & Scoring
- Detailed scoring metrics for each candidate:
  - Skills, experience, education, projects, keywords, ATS, grammar, soft skills, readability, cultural fit, domain relevance, certifications.
- Recommendation and fitment status generation.
- Sentiment analysis and tone detection in chat.
- Dashboard visualizing scores and metrics.

### 3.2 AI Chat Enhancements
- AI-driven candidate chat interface.
- Chat responses based on candidate resume and past answers.

### 3.3 Infrastructure & Storage
- Resume and chat data stored in MongoDB.

---

## 4. Planned Features (Phase 3 and Beyond)

### 4.1 AI-Powered Interviews
- Voice-based AI interview using Twilio.
- Video-based AI interview with AI-powered candidate monitoring (screening round).
- Cheating detection and behavior analysis during video interviews.
- Real-time monitoring using ML models (face detection, gaze tracking, lip-sync analysis).
- Transcript generation from voice/video interviews.
- Automated scoring based on responses, sentiment, and behavioral metrics.
- Recording and storing sessions with timestamped evidence.
- ML model wrappers stored in `models/` directory (face_detector.py, tracker.py, gaze_detector.py, audio_analyzer.py, lipsync.py).

### 4.2 Advanced Candidate Scoring
- Integration of transcript and voice/video analysis into scoring algorithm.
- Multi-dimensional scoring: technical, soft skills, cultural fit.
- Predictive fitment recommendation for job roles.

### 4.3 Notification & Alerts System
- Email and SMS notifications for candidates and recruiters.
- Automated alerts for new candidates, scores, and interview results.
- Integration with Google Calendar for scheduling interviews.

### 4.4 Dashboard & Analytics Enhancements
- Advanced charts and filters for candidate analysis.
- Multi-language support.
- AI insights and recommendations for recruiters.
- Integration with ATS (Greenhouse, Lever, etc.) for seamless data flow.

### 4.5 Security & Compliance
- Secure storage of sensitive candidate data.
- Encryption for tokens and PII data.
- GDPR and local compliance adherence.
- Audit logs for all user actions.

### 4.6 Developer & System Enhancements
- Versioned API endpoints (`v1`, `v2`) for future AI and scoring improvements.
- Improved error handling and logging.
- CI/CD integration for automated deployments.
- Unit and integration testing framework implementation (currently manual testing).
- Preliminary S3 / bucket implementations for recordings and session evidence.

---

## 5. Roadmap Chronology

| Phase | Timeline | Focus | Notes |
|-------|---------|-------|-------|
| Phase 1 | Completed | Core APIs, resume parsing, candidate/job CRUD, AI chat, dashboard | Stable backend and frontend, manual testing only |
| Phase 2 | Current | Candidate metrics, AI chat enhancements, session storage, scoring visualizations | Prepares for advanced AI interview features |
| Phase 3 | Next 2-3 months | AI voice/video interviews, transcript analysis, cheating detection, scoring, notifications, ATS integration, security enhancements | Requires ML/AI model integration and infrastructure scaling |
| Phase 4 | Future | Multi-language support, predictive analytics, automated testing, full CI/CD, enterprise-level deployment | Long-term goal for production-ready AI recruitment platform |

---

## 6. Notes & Best Practices

- **Separation of concerns:**
  - `app/models/` → database schemas.
  - `models/` → ML/AI wrappers.
- **Testing:** Currently manual, automated testing planned.
- **Documentation:** Keep API reference, testing strategy, and contribution guide updated with each phase.
- **Email contacts for queries:**
  - **Development & contribution**: Vishwajeet Mall – vishwajeet.mall@bee-logical.com, 
   Siddheshwar Mohite - siddheshwar.mohite@bee-logical.com
  - **Testing**: Ssanket Shinde – sanket.shinde@bee-logical.com,
  Vaibhavee Prajapat – vaibhavee.prajapat@bee-logical.com

---

**This roadmap is dynamic and will evolve as new AI features, recruitment strategies, and technology advancements are integrated into Smart HR Bot.**

