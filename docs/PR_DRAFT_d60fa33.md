# PR Title
Complete project stabilization: persistent DB, migrations, API wiring, and test cleanup

## Summary
This PR completes the unfinished project baseline and stabilizes backend/frontend integration.

It introduces persistent database-backed flows for authentication and projects, adds Alembic migration support, wires API gateway/frontend to real backend endpoints, improves local development setup, and fixes test/deprecation warnings.

## What Changed

### Backend Core
- Added SQLAlchemy persistent models for users and projects.
- Reworked database initialization and session handling for async DB usage.
- Added schema initialization flow and improved DB startup behavior.
- Implemented Alembic migration setup and initial migration:
  - users table
  - projects table
- Updated auth and user services to use persistent DB sessions.
- Updated auth, projects, analysis, and health routes.
- Replaced deprecated UTC usage with timezone-aware datetime calls.
- Strengthened security defaults and improved password/token handling.

### API Gateway
- Replaced mocked auth route behavior with backend-driven auth flow.
- Updated auth route integration behavior for consistent API responses.

### Frontend Web
- Connected auth store to real API login/logout flow.
- Connected dashboard create/list/delete project flows to backend APIs.
- Added API typing/interceptor improvements and state handling updates.

### DevOps / Local Development
- Added deployment docker-compose stack:
  - PostgreSQL
  - Redis
  - MongoDB
- Updated environment examples and backend local env defaults.
- Updated README with:
  - local start flow
  - Alembic migration commands

### Tests
- Updated backend tests and fixtures for DB-backed behavior.
- Stabilized auth tests with unique test users.
- Switched testclient import path/dependency usage to remove deprecations.
- Added required test dependency support.

## Files Added
- backend/core/alembic.ini
- backend/core/alembic/env.py
- backend/core/alembic/script.py.mako
- backend/core/alembic/versions/0001_create_users_projects.py
- backend/core/models/__init__.py
- backend/core/schemas/__init__.py
- backend/core/schemas/auth.py
- deployment/docker-compose.yml

## Verification
- Ran backend test suite:
  - python -m pytest backend/core/tests -q
  - Result: 7 passed

## Impact
- Project is now in a stable MVP state with persistent data.
- Local environment setup is reproducible.
- Core backend endpoints are functional and test-verified.
- Frontend and gateway are integrated with real backend flows.

## Follow-ups (Optional)
- Add CI workflow to run backend/frontend tests on PR.
- Introduce migration auto-check in CI.
- Add integration tests for API Gateway and frontend flows.
