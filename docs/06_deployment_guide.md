# 06_deployment_guide.md

## Smart HR Bot – Deployment Guide

This document provides guidance for deploying the **Smart HR Bot** project, including backend (FastAPI), frontend (React + Vite), and database configuration.  
It is written for developers who may not have deep CI/CD experience.

---

## 1. Prerequisites

- **Python 3.11+**  
- **Node.js 18+ and npm/yarn**  
- **Docker & Docker Compose**  
- **MongoDB** (local or cloud)  
- Internet connection for downloading dependencies

---

## 2. Backend Deployment

### 2.1 Environment Variables

The project uses a `.env` file for configuration. Example:

```env
# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log

# Application
APP_NAME=Smart-HR-Bot
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
API_V1_STR=/api/v1

# Database
MONGO_URI=mongodb://username:password@host:27017/?ssl=true
MONGO_DB_NAME=smart_hr_bot
ENCRYPTION_KEY=your_32_char_base64_key_here

# JWT
JWT_SECRET_KEY=supersecretjwtkey
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# OAuth / SSO (Google, Keka, Microsoft)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
KEKA_CLIENT_ID=your_keka_client_id
KEKA_CLIENT_SECRET=your_keka_client_secret
MS_CLIENT_ID=your_ms_client_id
MS_CLIENT_SECRET=your_ms_client_secret

# Email / Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password

# Rate Limiting
RATE_LIMIT_MAX=25
RATE_LIMIT_WINDOW=60

# GEMINI / LLM
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.0-flash
EMBEDDING_MODEL_NAME=gemini-embedding-001
```

> **Note:** The `ENCRYPTION_KEY` can be generated using the script `generate_and_save_key.py`.

---

### 2.2 Local Backend Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the backend locally:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

4. API will be accessible at: `http://127.0.0.1:8000/api/v1`

---

### 2.3 Docker Deployment

#### Dockerfile

- Already provided (`Dockerfile` in root).  
- Uses `python:3.11-slim`, installs dependencies, and runs `uvicorn`.

#### Docker Compose

```yaml
version: "3.9"

services:
  app:
    build: .
    container_name: smart_hr_bot_app
    restart: always
    env_file: .env
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    networks:
      - smart_hr_network
    dns:
      - 8.8.8.8
      - 8.8.4.4
      - 1.1.1.1
    extra_hosts:
      - "registry-1.docker.io:3.88.79.16"

networks:
  smart_hr_network:
    driver: bridge
```

**Run with Docker Compose:**

```bash
docker-compose up --build
```

- The backend will be accessible at `http://localhost:8000`.

> **Note:** Use Docker volumes for persisting logs or database dumps if needed.

---

## 3. Frontend Deployment (React + Vite)

### 3.1 Backend Proxy

The frontend `vite.config.ts` defines backend endpoints:

```ts
const backendUrls = {
  local: "http://localhost:8000",
  dev: "https://dev.api.smart-hr-bot.com",
  prod: "https://api.smart-hr-bot.com",
};
```

Change `activeBackend` depending on environment.

---

### 3.2 Local Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- Access at `http://localhost:5173` (Vite default).  
- API calls will be proxied to the backend via `vite.config.ts`.

---

### 3.3 Production Build

```bash
npm run build
```

- Builds optimized static files in `dist/`.  
- Serve using Nginx, Apache, or any static server.

---

## 4. Database

- MongoDB connection string is in `.env` (`MONGO_URI`).  
- Example local: `mongodb://localhost:27017`  
- Database name: `smart_hr_bot`

> **Tip:** Use cloud MongoDB (Atlas) for production. Ensure proper network access and credentials.

---

## 5. Logging

- Uses **Loguru** for backend logging.  
- Logs stored in `.env` path (`LOG_FILE=logs/app.log`) and stdout.  
- Rotate logs automatically every 10 MB, retain for 10 days.

---

## 6. Security / Encryption

- `ENCRYPTION_KEY` is 32-byte base64 for token encryption.  
- JWT tokens use `JWT_SECRET_KEY`.  
- OAuth keys are stored in `.env` (Google, Keka, Microsoft).

---

## 7. Notes for Production

1. Change `.env` variables for production credentials.  
2. Use `APP_ENV=production` and disable `DEBUG`.  
3. Consider a CI/CD pipeline:
   - Build Docker image
   - Push to registry
   - Deploy to server/cloud
4. Use HTTPS in production (via Nginx or Cloud provider).  
5. Ensure environment variables and secrets are not hardcoded.  
6. Database backups and monitoring recommended.  

---

## 8. References

- Backend Models: `app/models/*.py`  
- DB Operations: `app/core/db.py`  
- Logger Setup: `app/utils/logger.py`  
- Frontend Config: `vite.config.ts`

---

> ✅ With this guide, you can run your Smart HR Bot locally using Docker or directly, and prepare for production deployment.