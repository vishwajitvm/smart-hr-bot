# 04_api_reference.md

# Smart HR Bot - API Reference

This document provides a comprehensive reference for all APIs available in the Smart HR Bot system, including backend FastAPI routes, frontend calls (Axios), and special monitoring endpoints.

---

## 1. Status APIs

### 1.1 Health Check
- **Endpoint:** `/health`
- **Method:** GET
- **Description:** Lightweight JSON health check for core system components.
- **Response Example:**
```json
{
  "app": "ok",
  "mongodb": "ok",
  "logging": "ok",
  "env": "ok",
  "network": "ok",
  "api_hits": 12
}
```

### 1.2 System Health Dashboard
- **Endpoint:** `/system-health`
- **Method:** GET
- **Description:** HTML-based dashboard with detailed health status of MongoDB, logging, environment variables, network, and internal APIs. Auto-refresh every 5 seconds.
- **Response:** HTML page

---

## 2. Resume APIs

### 2.1 Upload Resume
- **Endpoint:** `/api/resume/upload`
- **Method:** POST
- **Request:** `multipart/form-data` with key `file`
- **Frontend Example (Axios):**
```ts
import { uploadResume } from "./services/api";

const response = await uploadResume(file);
console.log(response.data);
```
- **Response:** Parsed resume JSON

---

## 3. Candidate APIs

### 3.1 Submit Candidate Details
- **Endpoint:** `/api/candidates/`
- **Method:** POST
- **Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890"
}
```
- **Frontend Example (Axios):**
```ts
import { submitCandidateDetails } from "./services/api";
await submitCandidateDetails(candidateData);
```

### 3.2 Fetch All Candidates
- **Endpoint:** `/api/candidates/`
- **Method:** GET
- **Response:** Array of candidate objects

### 3.3 Fetch Candidate by ID
- **Endpoint:** `/api/candidates/{id}`
- **Method:** GET

### 3.4 Update Candidate
- **Endpoint:** `/api/candidates/{id}`
- **Method:** PUT

### 3.5 Delete Candidate
- **Endpoint:** `/api/candidates/{id}`
- **Method:** DELETE

### 3.6 Inactivate Candidate
- **Endpoint:** `/api/candidates/{id}/inactivate/`
- **Method:** PATCH

---

## 4. Jobs APIs

### 4.1 Fetch All Jobs
- **Endpoint:** `/api/jobs/`
- **Method:** GET

### 4.2 Fetch Job by ID
- **Endpoint:** `/api/jobs/{id}`
- **Method:** GET

### 4.3 Create Job
- **Endpoint:** `/api/jobs/`
- **Method:** POST

### 4.4 Update Job
- **Endpoint:** `/api/jobs/{id}`
- **Method:** PUT

### 4.5 Delete Job
- **Endpoint:** `/api/jobs/{id}`
- **Method:** DELETE

### 4.6 Update Job Status
- **Endpoint:** `/api/jobs/{id}/status`
- **Method:** PATCH
- **Request Body:**
```json
{ "status": 1 }
```

### 4.7 Generate Job Details with AI
- **Endpoint:** `/api/ai/jobs/generate`
- **Method:** POST
- **Request Body:**
```json
{ "title": "Frontend Developer" }
```
- **Response:** Structured JSON job description

---

## 5. Candidate Scoring APIs

### 5.1 Generate Candidate Score
- **Endpoint:** `/api/candidate-scoring/generate-score`
- **Method:** POST
- **Request Body:**
```json
{ "candidate_id": "abc123" }
```

### 5.2 Fetch Candidates With Scores
- **Endpoint:** `/api/candidates-listing-with-score/list`
- **Method:** POST
- **Request Body:**
```json
{
  "page": 1,
  "limit": 10,
  "filters": {}
}
```

### 5.3 Fetch Candidate Score By ID
- **Endpoint:** `/api/candidates-listing-with-score/get-candidate-by-id`
- **Method:** POST
- **Request Body:**
```json
{ "candidate_id": "abc123" }
```

### 5.4 Candidate Chat (AI Recruiter)
- **Endpoint:** `/api/candidates-listing-with-score/chat`
- **Method:** POST
- **Request Body:**
```json
{
  "candidate": { "id": "abc123", "name": "John Doe" },
  "question": "What is your experience with React?"
}
```

---

## 6. LLM / AI APIs

### 6.1 LLM Interaction
- **Endpoint:** `/api/llm/...` (multiple routes)
- **Description:** Interact with Gemini LLM for chat, resume parsing, or job generation.

---

## 7. Special / Planned APIs

### 7.1 Logs Viewer
- **Endpoint:** `/log`
- **Description:** Future endpoint for viewing application logs in a UI with filters, pagination, and search.

### 7.2 Voice Calling / Twilio Integration
- **Description:** Future endpoints for scheduling & conducting voice interviews, collecting scoring data automatically.

### 7.3 Cheating Detection
- **Description:** Future endpoint using OpenCV + YOLO + AI/ML to monitor candidates in real-time during interviews.

---

## 8. Notes

- All API responses follow standard JSON conventions unless explicitly returning HTML.
- Use `Content-Type: application/json` for all JSON POST/PUT/PATCH requests.
- File uploads must use `multipart/form-data`.
- Axios frontend calls use the `/api` base path.
- All future AI/ML features (voice interview, scoring, cheating detection) will be added in Phase 2/3.

---

**Editable:** Add more endpoints as backend features grow, including `/auth`, `/calendar`, `/notifications`, etc.