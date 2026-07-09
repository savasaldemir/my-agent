# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-alpha.1] - 2026-07-09

### Added
- Persistent database models for users and projects in backend core
- Alembic migration infrastructure and initial migration for users/projects tables
- Deployment compose stack for local PostgreSQL, Redis, and MongoDB
- PR draft documentation for stabilization changes

### Changed
- Auth and project flows migrated from in-memory behavior to persistent DB-backed behavior
- API Gateway auth routes wired to backend auth endpoints instead of mock responses
- Frontend auth and project dashboard flows integrated with real backend APIs
- README updated with one-command local infrastructure startup and Alembic usage commands
- Test setup updated for isolated DB usage with stable fixtures and unique auth test data

### Fixed
- Removed datetime.utcnow usage in backend JWT and health code paths by switching to timezone-aware timestamps
- Resolved Pydantic v2 settings deprecation in configuration handling
- Resolved test client deprecation path and ensured clean backend test execution
- Closed incomplete TODO-level behavior in core analysis/projects/auth implementation paths

## [1.0.0-alpha] - 2026-07-08

### Added
- Initial project setup
- Monorepo structure with npm workspaces
- Backend core engine (Python FastAPI)
- API Gateway (Node.js Express)
- Frontend web app (React + Vite)
- CLI tool
- Docker configuration
- GitHub Actions CI/CD workflows
- IDE plugins skeleton
- SDK for multiple languages

### Planned
- Code analysis engine
- Automatic bug fixing
- Testing framework integration
- Deployment automation
- Mobile app (React Native)
- Desktop app (Electron)
- VS Code extension
- JetBrains plugin
- System daemon
