# Testing guide

Backend: from `backend/`, install `requirements.txt` and run `python -m pytest -q`. AI tests verify curated skill extraction, deterministic scoring/explanation, and roadmap ordering. API tests verify registration, login, protected identity, and unauthenticated denial.

Frontend: from `frontend/`, run `npm install`, `npm test`, and `npm run build`. The current UI test checks the unauthenticated redirect to sign-in. CI executes both suites and the production build on pushes and pull requests to `main`/`develop`.

A full file-upload-to-report integration test and multi-user isolation matrix are still required before production acceptance; do not interpret the current focused tests as full acceptance coverage.
