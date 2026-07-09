## 1.0.0-alpha.1

Stabilization alpha release that completes the unfinished baseline and makes the project runnable end-to-end with persistent state.

### Highlights
- Stabilized the unfinished baseline into a working MVP.
- Migrated core auth and project flows to persistent DB-backed behavior.
- Added Alembic migration infrastructure and initial schema migration.
- Connected API gateway and frontend to live backend auth and project endpoints.
- Standardized local setup with PostgreSQL, Redis, and MongoDB via docker-compose.

### Included Changes
- Backend:
  - Added SQLAlchemy models for users and projects.
  - Completed auth, projects, and analysis route implementations.
  - Improved async database initialization and session handling.
  - Replaced deprecated UTC usage with timezone-aware datetime handling.
- API Gateway:
  - Replaced mocked auth behavior with backend-proxied auth flow.
- Frontend:
  - Wired auth and dashboard project actions to real API endpoints.
- Developer Experience:
  - Updated setup documentation and migration commands.
  - Stabilized DB-backed test setup.

### Verification
- Backend tests: 7 passed.

### Upgrade Notes
- Ensure async DB URL format is used where applicable:
  - `postgresql+asyncpg://...`
- Apply migrations before first run in a fresh environment:
  - `alembic upgrade head`

### Pre-release
This is an alpha pre-release intended for validation before stable release.
