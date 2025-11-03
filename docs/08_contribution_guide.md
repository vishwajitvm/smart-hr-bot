# 08_contribution_guide.md

# Contribution Guide for Smart HR Bot

---

## 1. Getting Started

To contribute to this project, follow these steps:

1. **Fork the repository** from Azure DevOps:
   ```bash
   https://BeeLogical-APP@dev.azure.com/BeeLogical-APP/InterviewBot/_git/InterviewBot
   ```

2. **Clone your fork locally:**
   ```bash
   git clone https://dev.azure.com/YOUR_USERNAME/InterviewBot/_git/InterviewBot
   cd InterviewBot
   ```

3. **Install backend dependencies:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

5. **Set up environment variables:**
   - Copy `.env.example` to `.env` in the backend folder.
   - Fill in required keys (MongoDB URI, JWT secret, OAuth keys, etc.).

6. **Run locally:**
   - **Backend:**
     ```bash
     uvicorn app.main:app --reload
     ```
   - **Frontend:**
     ```bash
     npm run dev
     ```

---

## 2. Branching Strategy

- **main** – Stable production-ready code
- **develop** – Active development branch
- **feature/your-feature-name** – New features
- **bugfix/issue-id** – Bug fixes
- **hotfix/issue-id** – Emergency fixes

**Always branch off `develop` for new work.**

---

## 3. Code Style


- **React frontend:**
  - Use **ESLint + Prettier** rules.
  - Functional components with hooks.
  - Avoid inline styles; use bulma or CSS modules.

- **Commit messages:**
  - Use conventional commits style:
    ```
    feat: add new AI chat endpoint
    fix: resolve token encryption bug
    docs: update README
    style: format code according to ESLint/PEP8
    refactor: restructure API modules
    test: add unit tests for new endpoints
    chore: update dependencies or scripts
    ```

---

## 4. Pull Requests

1. Make sure your branch is **up-to-date with `develop`**.
2. Run all tests before committing.
3. Push your branch to your fork.
4. Open a **Pull Request** to `develop` in the main repo.
5. Include a clear **description** of your changes and reference any related issues.
6. PR will be reviewed by the team; address feedback before merging.

---

## 5. Testing

- **Backend:**
  ```bash
  pytest tests/
  ```
- **Frontend:**
  ```bash
  npm run test
  ```

NOTE: Currently test cases are not writen

---

## 6. Code Review Checklist

- Code is clean and readable.
- Follows project coding standards.
- Proper error handling and logging.
- No hardcoded secrets.
- Documentation updated if necessary.

---

## 7. Security & Secrets

- Never commit `.env` files or secrets to the repository.
- Use secure methods to store and share sensitive keys.
- Use the encryption utilities provided in `app/core/db.py` for storing tokens.

---

## 8. Additional Notes

- For major feature changes, discuss first.
- Keep branches focused; one feature per branch.
- Update documentation for new APIs or database changes.

---

## Contact
For any questions, clarifications, or contribution approvals, reach out to:
**Vishwajit** – vishwajeet.mall@bee-logical.com

---

**Happy contributing!**

