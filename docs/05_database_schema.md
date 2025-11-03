# 05_database_schema.md

## Overview
This document provides an overview of the **MongoDB database schema** for the Smart HR Bot project.  
It describes the main collections, their purposes, relationships, and references to model files for field-level details.  

> **Note:** MongoDB is schemaless, so fields can evolve. Always refer to the Pydantic models for the current structure.

---

## Collections

### 1. Users (`users`)
- **Purpose:** Stores user accounts (HRs, admins, etc.).
- **Relationships:**
  - `tokens` collection → stores authentication/refresh tokens for users.
- **Reference:** `app/models/user.py`  
- **Notes:** User roles, credentials, and profile info are defined in the model.

---

### 2. Candidates (`candidates`)
- **Purpose:** Stores candidate profiles, resumes, and additional metadata.
- **Relationships:**
  - `jobs` → each candidate may be linked to a job via `job_id`.
  - `candidate_scores` → stores scoring and fitment info per candidate.
  - `candidate_chats` → stores AI chat logs per candidate.
- **Reference:** `app/models/candidate.py`
- **Notes:** Supports extra unstructured fields via `extra_data`.

---

### 3. Jobs (`jobs`)
- **Purpose:** Stores job postings, details, and AI-generated suggestions.
- **Relationships:**
  - `candidates` → candidates link to jobs via `job_id`.
  - `candidate_scores` → candidate fitment scoring related to jobs.
- **Reference:** `app/models/job.py` & `JobAIResponse`
- **Notes:** Jobs may have multiple candidates; supports AI-driven job generation.

---

### 4. Candidate Scores (`candidate_scores`)
- **Purpose:** Stores scoring information for candidates.
- **Relationships:**
  - `candidates` → linked by `candidate_id`.
  - `jobs` → linked by `job_id` (optional).
- **Reference:** `app/models/scoring.py`
- **Notes:** Includes detailed scoring breakdown, sentiment, fitment, strengths/weaknesses, and versioning.

---

### 5. Candidate Chats (`candidate_chats`)
- **Purpose:** Stores AI-powered chat logs for candidate interactions.
- **Relationships:**
  - `candidates` → linked by `candidate_id`.
  - `jobs` → linked by `job_id`.
- **Reference:** `app/models/candidate_chat.py`
- **Notes:** Stores questions, responses, metadata, timestamps, and logs AI interactions.

---

### 6. Tokens (`tokens`, `keka_tokens`)
- **Purpose:** Stores encrypted OAuth and integration tokens.
- **Relationships:**
  - Linked to `users` via `user_id`.
- **Reference:** `app/core/db.py` for encryption logic.
- **Notes:** Supports refresh tokens; encrypted using Fernet.

---

### 7. Chat Logs & AI Scoring (Derived/Related)
- **Purpose:** Combined view from `candidate_chats` + `candidate_scores` + `candidates` for analytics.
- **Notes:** Used for dashboards, AI-assisted scoring, and recruiter insights.

---

## Relationships Summary
- `users` ↔ `tokens`  
- `candidates` ↔ `jobs`  
- `candidates` ↔ `candidate_scores`  
- `candidates` ↔ `candidate_chats`  
- `jobs` ↔ `candidate_scores`  
- `jobs` ↔ `candidate_chats`  

> These are **logical relationships**, as MongoDB doesn’t enforce foreign keys. Relations are managed at the application layer.

---

## Notes
- Always refer to the **Pydantic models** for up-to-date field definitions.  
- Collections can evolve; the schema is flexible and may change based on feature updates.  
- Use this document as a **high-level reference** rather than a field-level manual.
