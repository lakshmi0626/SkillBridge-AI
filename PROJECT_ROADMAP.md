# Project roadmap

## MVP delivered in this repository
- Account registration/login, protected user-owned workflows.
- PDF/DOCX extraction, curated skill evidence, job analyzer, deterministic explainable match scoring.
- Skill gaps, recommendations, learning milestone generation, progress updates, dashboard and PDF reports.
- PostgreSQL Docker deployment path, SQLite local path, migrations, focused tests and CI.

## Next increments
1. Add profile/education/experience extraction with evidence spans and confidence, plus OCR worker for scanned PDFs.
2. Add refresh token rotation, logout revocation, password reset/email provider, rate limiting and audit logs.
3. Persist normalized skills/categories, role catalog, recommendation snapshots, roadmaps/milestones, notifications and saved jobs.
4. Add resume versions/default selection and encrypted object storage lifecycle controls.
5. Add semantic model experiments with offline benchmark, model versioning and opt-in external inference.
6. Expand admin management, charts, filtering/pagination, frontend accessibility and multi-user end-to-end tests.
7. Add deployment environments, observability, backup/restore drills and security scanning.
