# SkillBridge AI

**Resume intelligence, explainable career matching, and skill development.** SkillBridge AI is a full-stack career workspace that extracts evidence from a candidate's PDF/DOCX resume, compares it with a saved job description, explains a deterministic compatibility score, identifies missing skills, and creates a practical learning sequence.

> Matching is an advisory comparison based on document text and a curated skill vocabulary. It is not an employer ATS score and does not predict or guarantee hiring outcomes.

## MVP capabilities

- JWT registration, login, current-user identity, logout client flow, and role-gated admin endpoints.
- Private PDF/DOCX upload with file size/type checks and text extraction; scanned PDF OCR is not yet supported.
- Curated technical skill extraction and job description skill parsing.
- Explainable score: 65% required skill coverage + 10% preferred skill coverage + 25% TF-IDF cosine similarity.
- Missing and additional skills, role recommendations, and gap-driven learning milestones.
- Account-scoped dashboard, progress tracking, and authorized PDF reports.
- PostgreSQL via Docker Compose; SQLite is the zero-setup local development default.
- Alembic migration, pytest/Vitest suites, Dockerfiles, and GitHub Actions CI.

## Architecture

- `frontend/`: React 18, Vite, React Router, Axios, Recharts dependency, Lucide icons, responsive neutral UI.
- `backend/`: FastAPI REST API, SQLAlchemy 2, Pydantic, JWT, private local file storage, PDF/DOCX parsing, PDF reports.
- `ai-engine/`: standalone algorithm modules and evaluation tests (core MVP implementation lives in `backend/app/services/ai.py`).
- `database/`: schema and seed assets.

See `docs/ARCHITECTURE.md`, `docs/DATABASE_SCHEMA.md`, and `docs/API_DOCUMENTATION.md`.

## Local setup (Windows PowerShell)

### Backend

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
$env:SECRET_KEY = "replace-with-a-long-random-development-secret"
py -m alembic upgrade head
py -m uvicorn app.main:app --reload
```

If you only have Python 3.14 installed, use `py -m venv .venv`; the Docker and CI environments use Python 3.12 for dependency compatibility. For local SQLite, no PostgreSQL server is required.

### Frontend (new terminal)

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. API docs: http://localhost:8000/docs. Health: http://localhost:8000/health.

### Docker / PostgreSQL

```powershell
Copy-Item .env.example .env
# Edit .env and set unique POSTGRES_PASSWORD and SECRET_KEY values.
docker compose up --build
```

Frontend: http://localhost:8080 · API: http://localhost:8000/docs. Persistent database and resume volumes are configured.

## Tests

```powershell
cd backend
py -m pip install -r requirements.txt
py -m pytest -q
```

```powershell
cd frontend
npm install
npm test
npm run build
```

## Security notes

- Passwords are Argon2-hashed; access tokens are signed JWTs with expiration.
- All resume, job, analysis, progress, and report lookups are scoped to the authenticated user.
- Resume files are stored outside the public frontend and never served as public static assets.
- Set a unique `SECRET_KEY`, restrict CORS, use HTTPS, configure a private durable object store, malware scanning, rate limiting, and secret management before production.
- The initial admin management endpoints are read-only; promote an administrator through a controlled database operation. Never expose database credentials.
- Logout invalidates the client-held token by instructing the client to discard it; token denylisting/refresh rotation is future work.

## Current limitations

OCR for scanned resumes, refresh-token rotation, password reset/email delivery, full profile editing, admin write workflows, database-backed notifications, resume version/default management, richer entity extraction (education/experience/projects), semantic embedding models, and complete accessibility/mobile QA remain planned. The app deliberately reports only extracted evidence and does not fabricate experience or job vacancies.

## Git workflow

`main` is the stable line; `develop` is the integration line. Use focused `feature/*` branches and PRs with tests. Only genuine completed changes should be committed or merged. See `CONTRIBUTING.md`.

## License

MIT. See `LICENSE`.
