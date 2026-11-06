# Installation guide

See the root README for copy/paste PowerShell setup. The recommended reproducible deployment is Docker Compose with PostgreSQL 16. Local development defaults to SQLite and requires no database service. Set `SECRET_KEY` and `DATABASE_URL` through environment variables; never commit `.env`. Run Alembic migrations before serving the API. The React dev server runs on port 5173 and API on 8000.
