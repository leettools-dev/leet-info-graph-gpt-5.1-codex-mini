# leet-info-graph-gpt-5.1-codex-mini

> This project is being developed by an autonomous coding agent.

## Overview

Research Infograph Assistant helps users sign in with Google, submit research prompts, and receive AI-generated infographics backed by curated sources. The stack combines a FastAPI backend, a Vue 3 + TailwindCSS frontend, DuckDB for storage, and Google OAuth for authentication.

## Backend

### Structure

The backend is implemented as a FastAPI service under `backend/src/infograph`. Key directories include:

- `svc/`: API entry points and router grouping.
- `core/schemas/`: Pydantic models for users, sessions, sources, messages, and infographics.
- `stores/`: Abstract and DuckDB-backed stores for persistence.
- `services/`: Business logic layers such as auth, search, and infographic generation.

### Current Features

- Click-based CLI (`infograph.svc.main`) to start the service with configurable host, port, and log level.
- FastAPI application factory with OpenAPI docs and permissive CORS middleware.
- `HealthRouter` exposing `/api/v1/health`, returning the service status and version.
- Pytest suite covering the health endpoint to ensure the service is online.

### Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e backend
python -m infograph.svc.main --port 8000
```

Run the health check to confirm the backend is ready:

```bash
curl http://localhost:8000/api/v1/health
```

Run backend tests:

```bash
cd backend
python -m pytest tests/
```

## Features

- Added `SourceList` and `SourceCard` frontend components that fetch `/api/v1/sessions/{session_id}/sources` and display each source with clickable links.
- The session detail page now renders session metadata alongside fetched sources from the backend.
- Documented backend skeleton with FastAPI application factory, CLI entry point, and health endpoint so the service can be launched with `python -m infograph.svc.main --port 8000` and verified via `/api/v1/health`.

## Next Up

- scaffold the Vue 3 frontend (Vite + Element Plus + TailwindCSS)
- connect the frontend to the backend health check
- implement authentication, session management, and infographic rendering
