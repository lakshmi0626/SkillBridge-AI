# Architecture

## Runtime topology

The browser SPA calls the FastAPI REST service using bearer JWTs. FastAPI validates the token and scopes all user-owned queries by the authenticated `user_id`. SQLAlchemy persists relational data in PostgreSQL (Docker) or SQLite (local development). Uploaded originals are stored in a private server-side directory; extracted text and skill evidence are persisted for analysis. Report PDFs are generated on demand from authorized analysis records.

## Request flow

1. React obtains an access token through registration/login and stores it in browser local storage for this MVP.
2. Axios adds the bearer token to API requests.
3. FastAPI validates JWT signature and expiration, loads the user, and enforces owner scoping.
4. Resume service validates extension/size and extracts text from PDF/DOCX.
5. Skill service normalizes text and detects terms from a curated, auditable vocabulary.
6. Matching service combines required/preferred skill coverage with TF-IDF cosine similarity.
7. Analysis and progress data are saved; roadmap and PDF report are generated from those saved records.

## Boundaries and production evolution

The `backend/app/services` package owns domain logic. `ai-engine/` is reserved for separately deployable/evaluable algorithms. For production, move uploads to private object storage, use asynchronous processing for OCR/large documents, add refresh-token rotation/denylisting, rate limits, structured audit events, and a secrets manager. Add an embedding model only after offline evaluation and explicit model/version tracking.
