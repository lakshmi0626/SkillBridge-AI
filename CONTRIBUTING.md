# Contributing

1. Branch from `develop` using `feature/<short-scope>` or `fix/<short-scope>`.
2. Keep changes scoped and add/update tests.
3. Run backend pytest, frontend Vitest and Vite build.
4. Open a PR to `develop` with context, changed modules, test evidence, migration notes and security implications.
5. Merge only after review and passing CI. Promote a verified release from `develop` to `main`.

Use conventional commits such as `feat(resume): validate and extract docx uploads` and `test(matching): cover missing skill calculation`. Never add secrets, real resumes or personal data to Git.
