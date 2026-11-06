# API reference

Base URL: `http://localhost:8000/api`. Interactive OpenAPI: `/docs`. Protected endpoints require `Authorization: Bearer <access_token>`.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Create account and return JWT |
| POST | `/auth/login` | Verify credentials and return JWT |
| POST | `/auth/logout` | Client token-discard acknowledgement |
| GET | `/auth/me` | Current account |
| POST | `/resumes/upload` | Upload PDF/DOCX multipart field `file` |
| GET | `/resumes` | List own resumes |
| GET/DELETE | `/resumes/{id}` | Read own resume metadata/text or delete |
| POST | `/jobs/analyze` | Save job text and extract skills |
| GET | `/jobs`, `/jobs/{id}` | List/read own job descriptions |
| POST | `/matching/analyze?resume_id=&job_id=` | Persist matching analysis |
| GET | `/matching/history`, `/matching/{id}` | Own analysis history/detail |
| GET | `/skills`, `/skills/gaps`, `/skills/progress` | Own skill evidence/gaps/progress |
| PATCH | `/skills/progress?skill=&status_value=` | Update a skill status |
| GET | `/career/recommendations` | Role fit from own resume skills |
| POST | `/career/roadmaps?analysis_id=` | Generate roadmap from own analysis gaps |
| GET | `/career/roadmaps` | Rebuild roadmaps from own analyses |
| PATCH | `/career/roadmaps/{analysis_id}/progress?skill=&status_value=` | Update roadmap skill progress |
| GET | `/dashboard/summary`, `/dashboard/analytics` | Own dashboard data |
| GET | `/reports/{id}/pdf` | Download own report PDF |
| GET | `/admin/users`, `/admin/analytics` | Admin-only read endpoints |

Validation errors use FastAPI's standard 422 response; unauthenticated requests return 401, forbidden admin requests 403, missing/foreign records 404, duplicate email 409, unsupported upload type 415, and oversized uploads 413.
