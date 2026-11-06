# Security

- Hash passwords with bcrypt and use short-lived signed JWT access tokens.
- Keep the JWT secret in environment configuration; replace the development default.
- Validate upload extension, byte size, extraction outcome and use random server filenames.
- Keep uploaded files outside the frontend public directory.
- Enforce ownership filters on resume, job, analysis, roadmap, progress and report operations.
- Use parameterized SQLAlchemy queries and allow only configured CORS origins.
- Production checklist: HTTPS, strong secrets, rate limits, token revocation/refresh rotation, malware scanning, OCR sandboxing, encrypted private object storage, audit trails, backup/restore tests, CSP/security headers, dependency scanning, and privacy retention/deletion policy.
