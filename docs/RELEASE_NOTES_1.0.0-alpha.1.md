# Release Notes - 1.0.0-alpha.1

Release date: 2026-07-09

## Highlights
- Stabilized unfinished baseline into a working MVP.
- Migrated core auth/project flows from in-memory behavior to persistent DB-backed behavior.
- Added migration infrastructure and initial schema migration.
- Wired API gateway and frontend to real backend auth/project endpoints.
- Standardized local development setup with containerized infrastructure services.

## Included Changes

### Backend Core
- Added persistent SQLAlchemy models for users and projects.
- Added Alembic setup and initial migration for users/projects.
- Improved database initialization and async session handling.
- Completed auth/projects/analysis route implementations.
- Replaced deprecated UTC calls with timezone-aware datetime usage.

### API Gateway
- Replaced mocked auth behavior with backend-driven auth flow.

### Frontend Web
- Connected auth store and dashboard project actions to live API endpoints.

### Local Development
- Added deployment docker-compose stack for PostgreSQL, Redis, and MongoDB.
- Updated README with local startup and migration commands.

### Quality
- Updated and stabilized backend test setup for DB-backed flows.
- Backend tests passing: 7/7.

## Upgrade Notes
- Ensure environment uses async DB URL format where applicable:
  - postgresql+asyncpg://...
- Apply migrations before running in a fresh environment:
  - alembic upgrade head

## Verification
- Command: python -m pytest backend/core/tests -q
- Result: 7 passed
