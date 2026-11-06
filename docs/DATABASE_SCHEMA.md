# Database schema

| Table | Purpose | Ownership / constraints |
|---|---|---|
| users | Accounts, role, active state | unique indexed email |
| resumes | Private resume metadata, extracted text and skills | FK users; owner indexed |
| job_descriptions | User-saved role/company/description and extracted skills | FK users; owner indexed |
| analyses | Explainable score and skill evidence | FK user/resume/job; owner indexed |
| skill_progress | Per-user status for each skill | FK users; owner indexed |

All tables use integer primary keys and UTC timestamps where applicable. User deletion cascades to owned data. Resume deletion cascades its analyses; job deletion cascades its analyses. `JSON` columns hold extracted skill lists and matching evidence, while normalized ownership and workflow relationships remain relational. Schema changes are managed through Alembic (`backend/migrations`).

The requested extended entities (profiles, resume versions, skill taxonomy/category tables, role catalog, recommendations, persisted roadmap/milestones, saved jobs, notifications, audit logs) are staged for subsequent migrations; the current MVP uses a small, normalized core to complete the critical workflow safely.
