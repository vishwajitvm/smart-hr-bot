# 07_setup_instructions.md

# Smart HR Bot - Setup Instructions

This document provides detailed setup instructions to get the **Smart HR Bot** running locally or on a server. It is designed for developers working with **Azure DevOps** and Docker-based environments.

---

## Prerequisites
Ensure the following are installed on your system:

- **Git** (>= 2.40)
- **Docker** (>= 24.x)
- **Docker Compose** (>= 2.17)
- **Python** (>= 3.11)
- **Node.js** (>= 20.x)
- **npm** or **yarn** (>= 10.x)

---

## 1. Clone the Repository

Use your Azure DevOps repository URL to clone the project:

```bash
git clone https://BeeLogical-APP@dev.azure.com/BeeLogical-APP/InterviewBot/_git/InterviewBot
cd InterviewBot
```

Make sure you have the required permissions in Azure DevOps to clone the repository.

---

## 2. Backend Setup (FastAPI / Python)

### 2.1. Environment

1. Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

2. Update environment variables in `.env`:

- MongoDB connection
- JWT secrets
- OAuth / SSO credentials (Google, Keka, Microsoft)
- SMTP credentials
- Gemini / LLM API key
- Rate limiting and other configs

> **Tip:** Use the provided Python script to generate an encryption key for sensitive data:

```bash
python scripts/generate_encryption_key.py
```

This will update `ENCRYPTION_KEY` in your `.env`.

---

### 2.2. Python Environment

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
```

2. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 2.3. Running Backend Locally

Start FastAPI development server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000/api/v1`

---

## 3. Frontend Setup (React + Vite)

### 3.1. Install Node.js Dependencies

Make sure you have Node.js v18+ and npm/yarn installed.

```bash
cd frontend
npm install
# or
yarn install
```

---

### 3.2. Configure Backend URL

Edit `vite.config.ts` to point to your backend:

```ts
const backendUrls = {
  local: "http://localhost:8000",
  local127: "http://127.0.0.1:8000",
  dev: "https://dev.api.smart-hr-bot.com",
  test: "https://test.api.smart-hr-bot.com",
  prod: "https://api.smart-hr-bot.com",
}

const activeBackend = backendUrls.local
```

---

### 3.3. Run Frontend

```bash
npm run dev
# or
yarn dev
```

Frontend will be available at `http://localhost:5173` (default Vite port).

---

## 4. Docker Setup

### 4.1. Build Docker Image

```bash
docker-compose build
```

### 4.2. Run Docker Containers

```bash
docker-compose up -d
```

- Backend will be available on `http://localhost:8000`
- Uses `.env` file for configuration
- Logs stored at `logs/app.log`

---

## 5. Database (MongoDB)

- Ensure MongoDB is running locally or accessible remotely.
- Update `MONGO_URI` in `.env` accordingly:

```env
MONGO_URI=mongodb://username:password@host:27017/?ssl=true
MONGO_DB_NAME=smart_hr_bot
```

- Collections used:

  - `users`
  - `candidates`
  - `jobs`
  - `candidate_scores`
  - `candidate_chats`
  - `tokens`
  - `keka_tokens`
  - `chat_logs`

> **Note:** MongoDB Atlas or self-hosted MongoDB can be used.

---

## 6. Logging

- Configured via `app/utils/logger.py`
- Logs are stored in `logs/app.log`
- Rotation: 10 MB
- Retention: 10 days
- Console output included

---

## 7. Encryption & Security

- Encryption key stored in `.env` (`ENCRYPTION_KEY`)
- Tokens are encrypted using `cryptography.fernet`
- JWT authentication configured with `JWT_SECRET_KEY` and `JWT_ALGORITHM`

> **Important:** Never commit `.env` to version control.

---

## 8. Running Tests (Optional)

- Add your unit tests under `tests/`
- Run with:

```bash
pytest
```

- Or, for FastAPI API tests:

```bash
pytest -s --tb=short
```

---

## 9. Azure DevOps Integration

1. Push local changes:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

2. Setup CI/CD pipeline in Azure DevOps:

- Create a pipeline in DevOps using `azure-pipelines.yml` (not included here)
- Steps typically include:
  - Install Python / Node
  - Install dependencies
  - Run tests
  - Build Docker image
  - Push Docker image to Azure Container Registry
  - Deploy to Azure App Service or Kubernetes

> **Tip:** Use staging / dev environments first before production.

---

## 10. Notes

- Ensure your backend `.env` matches the environment (local/dev/prod)
- Update frontend backend URL when switching environments
- Use Docker for consistent local or server environments
- Logs and encryption are handled automatically, just ensure `.env` keys are set

---

## 11. References

- FastAPI Docs: https://fastapi.tiangolo.com
- MongoDB Docs: https://docs.mongodb.com
- Docker Docs: https://docs.docker.com
- Vite + React: https://vitejs.dev
- Azure DevOps: https://learn.microsoft.com/en-us/azure/devops/

---

## 12. NOTE: Troubleshooting
- If `docker-compose up` fails, ensure Docker Daemon is running.
- If dependencies fail, delete `node_modules` or `__pycache__` and reinstall.
- Use `docker-compose logs -f` to debug running containers.
