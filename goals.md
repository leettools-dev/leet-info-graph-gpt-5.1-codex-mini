---
project_name: leet-info-graph-gpt-5.1-codex-mini
created_at: 2026-02-05T01:28:23.933549+00:00
status: in_progress
---

# Goal Description

# Research Infograph Assistant - Project Goals

## Overview

Build a full-stack web application that lets users sign in with Google, submit research prompts, 
and receive AI-generated infographics with supporting sources. Users can browse their research 
history and export results.

---

## Technology Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Backend | FastAPI (Python 3.11+) | Follow patterns in `/app/guides/fastapi.dev.md` |
| Frontend | Vue 3 + Composition API | Follow patterns in `/app/guides/frontend.dev.md` |
| UI Components | Element Plus + TailwindCSS | Auto-imported, CSS variables for theming |
| Database | DuckDB | Embedded, use `DuckDBClient` patterns |
| Auth | Google OAuth 2.0 | Google Identity Services (GIS) |
| Image Storage | Local filesystem | `/workspace/data/infographics/` |

---

## Project Structure

### Backend (`/workspace/backend/`)

```
backend/
├── src/
│   └── infograph/
│       ├── __init__.py
│       ├── svc/
│       │   ├── __init__.py
│       │   ├── main.py                    # CLI entry point
│       │   ├── api_service.py             # FastAPI app setup
│       │   ├── api_router_base.py         # Base router class
│       │   └── api/
│       │       └── v1/
│       │           ├── __init__.py
│       │           ├── api.py             # Router aggregator
│       │           └── routers/
│       │               ├── __init__.py
│       │               ├── health_router.py
│       │               ├── auth_router.py
│       │               ├── session_router.py
│       │               ├── source_router.py
│       │               └── infographic_router.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── schemas/
│       │       ├── __init__.py
│       │       ├── user.py
│       │       ├── research_session.py
│       │       ├── source.py
│       │       ├── infographic.py
│       │       └── message.py
│       ├── stores/
│       │   ├── __init__.py
│       │   ├── abstract_user_store.py
│       │   ├── abstract_session_store.py
│       │   ├── abstract_source_store.py
│       │   ├── abstract_infographic_store.py
│       │   └── duckdb/
│       │       ├── __init__.py
│       │       ├── user_store_duckdb.py
│       │       ├── session_store_duckdb.py
│       │       ├── source_store_duckdb.py
│       │       └── infographic_store_duckdb.py
│       └── services/
│           ├── __init__.py
│           ├── auth_service.py            # Google OAuth handling
│           ├── search_service.py          # Web search + source extraction
│           └── infographic_service.py     # Infographic generation
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_health_router.py
│   ├── test_auth_router.py
│   ├── test_session_router.py
│   └── test_stores/
│       └── test_user_store.py
├── pyproject.toml
└── README.md
```

### Frontend (`/workspace/frontend/`)

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/
│   │   ├── auth.js
│   │   ├── session.js
│   │   ├── source.js
│   │   └── infographic.js
│   ├── assets/
│   │   ├── main.scss
│   │   └── theme/
│   │       ├── index.scss
│   │       └── dark.scss
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInput.vue
│   │   │   ├── MessageList.vue
│   │   │   └── MessageBubble.vue
│   │   ├── source/
│   │   │   ├── SourceCard.vue
│   │   │   └── SourceList.vue
│   │   └── infographic/
│   │       ├── InfographicViewer.vue
│   │       └── InfographicExport.vue
│   ├── composables/
│   │   ├── useAuth.js
│   │   └── useTheme.js
│   ├── i18n/
│   │   ├── en/
│   │   │   ├── common.js
│   │   │   ├── auth.js
│   │   │   ├── chat.js
│   │   │   └── index.js
│   │   ├── ja/
│   │   │   └── ...
│   │   ├── zh/
│   │   │   └── ...
│   │   └── index.js
│   ├── lib/
│   │   └── utils.js
│   ├── pages/
│   │   ├── auth/
│   │   │   └── LoginPage.vue
│   │   ├── chat/
│   │   │   └── ChatPage.vue
│   │   ├── history/
│   │   │   └── HistoryPage.vue
│   │   └── session/
│   │       └── SessionDetailPage.vue
│   ├── router/
│   │   └── index.js
│   ├── stores/
│   │   ├── index.js
│   │   └── modules/
│   │       ├── auth/
│   │       │   └── index.js
│   │       ├── chat/
│   │       │   └── index.js
│   │       └── session/
│   │           └── index.js
│   ├── utils/
│   │   └── request.js
│   ├── App.vue
│   ├── main.js
│   └── env.js
├── index.html
├── vite.config.js
├── tailwind.config.js
├── package.json
└── README.md
```

---

## Data Schemas (Pydantic Models)

### User

```python
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    name: str
    google_id: str

class User(BaseModel):
    user_id: str          # UUID
    email: str
    name: str
    google_id: str
    created_at: int       # Unix timestamp
    updated_at: int
```

### ResearchSession

```python
from typing import Literal, Optional
from pydantic import BaseModel

class ResearchSessionCreate(BaseModel):
    prompt: str

class ResearchSession(BaseModel):
    session_id: str       # UUID
    user_id: str
    prompt: str
    status: Literal["pending", "searching", "generating", "completed", "failed"]
    created_at: int
    updated_at: int

class ResearchSessionUpdate(BaseModel):
    status: Optional[Literal["pending", "searching", "generating", "completed", "failed"]] = None
```

### Source

```python
from pydantic import BaseModel
from typing import Optional

class SourceCreate(BaseModel):
    session_id: str
    title: str
    url: str
    snippet: str
    confidence: float     # 0.0 to 1.0

class Source(BaseModel):
    source_id: str        # UUID
    session_id: str
    title: str
    url: str
    snippet: str
    confidence: float
    fetched_at: int
```

### Infographic

```python
from pydantic import BaseModel
from typing import Optional, Any

class InfographicCreate(BaseModel):
    session_id: str
    template_type: str    # "basic", "stats", "timeline"
    layout_data: dict     # JSON with title, bullets, stats, etc.

class Infographic(BaseModel):
    infographic_id: str   # UUID
    session_id: str
    image_path: str       # Local file path
    template_type: str
    layout_data: dict
    created_at: int
```

### Message

```python
from pydantic import BaseModel
from typing import Literal

class MessageCreate(BaseModel):
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str

class Message(BaseModel):
    message_id: str       # UUID
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: int
```

---

## API Endpoints

### Health

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/v1/health` | Health check | `{"status": "ok", "version": "1.0.0"}` |

### Auth

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|--------------|----------|
| POST | `/api/v1/auth/google` | Exchange Google token | `{"credential": "..."}` | `{"user": User, "token": "jwt..."}` |
| GET | `/api/v1/auth/me` | Get current user | - | `User` |
| POST | `/api/v1/auth/logout` | Logout | - | `{"success": true}` |

### Sessions

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|--------------|----------|
| POST | `/api/v1/sessions` | Create session | `ResearchSessionCreate` | `ResearchSession` |
| GET | `/api/v1/sessions` | List user sessions | Query: `?limit=10&offset=0` | `list[ResearchSession]` |
| GET | `/api/v1/sessions/{session_id}` | Get session | - | `ResearchSession` |
| DELETE | `/api/v1/sessions/{session_id}` | Delete session | - | `{"success": true}` |

### Messages (Chat)

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|--------------|----------|
| POST | `/api/v1/sessions/{session_id}/messages` | Send message | `MessageCreate` | `Message` |
| GET | `/api/v1/sessions/{session_id}/messages` | Get messages | - | `list[Message]` |

### Sources

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/v1/sessions/{session_id}/sources` | Get sources | `list[Source]` |

### Infographic

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/v1/sessions/{session_id}/infographic` | Get infographic | `Infographic` |
| GET | `/api/v1/sessions/{session_id}/infographic/image` | Get image file | Binary (PNG) |
| GET | `/api/v1/sessions/{session_id}/export` | Export session | JSON or ZIP |

---

## Implementation Goals

### Phase 1: Skeleton & Auth

#### Goal 1: Backend Skeleton
Create the basic FastAPI backend structure with health endpoint.

**Tasks:**
- Initialize Python package structure under `backend/src/infograph/`
- Create `main.py` with Click CLI for starting server
- Create `api_service.py` with FastAPI app, CORS middleware
- Create `health_router.py` with `/api/v1/health` endpoint
- Add `pyproject.toml` with dependencies

**Acceptance Criteria:**
- `python -m infograph.svc.main --port 8000` starts the server
- `GET http://localhost:8000/api/v1/health` returns `{"status": "ok"}`
- pytest test passes for health endpoint

---

#### Goal 2: Frontend Skeleton
Create the basic Vue 3 frontend that connects to the backend.

**Tasks:**
- Initialize Vite + Vue 3 project
- Configure TailwindCSS and Element Plus
- Create router with placeholder pages (Login, Chat, History)
- Create `request.js` Axios instance pointing to backend
- Create health check API call on app load

**Acceptance Criteria:**
- `yarn dev` starts frontend on port 3001
- App shows "Backend Connected" status on successful health check
- Router navigates between placeholder pages

---

#### Goal 3: Database Stores
Set up DuckDB stores for all entities.

**Tasks:**
- Create abstract store interfaces for User, Session, Source, Infographic, Message
- Implement DuckDB stores following `DuckDBClient` patterns
- Create tables with proper schemas
- Write pytest tests for CRUD operations

**Acceptance Criteria:**
- Can create, read, update, delete all entity types
- All store tests pass
- Tables created automatically on first use

---

#### Goal 4: Google OAuth Login
Implement Gmail OAuth authentication flow.

**Tasks:**
- Backend: Create `auth_service.py` to verify Google tokens
- Backend: Create `auth_router.py` with `/auth/google` and `/auth/me` endpoints
- Backend: Generate JWT tokens for authenticated sessions
- Frontend: Create `LoginPage.vue` with Google Sign-In button
- Frontend: Create `useAuth.js` composable for auth state
- Frontend: Create `auth` Pinia store
- Frontend: Add auth guard to router

**Acceptance Criteria:**
- User can click "Sign in with Google" button
- After Google auth, user is redirected to Chat page
- User info (name, email) is displayed in header
- Unauthenticated users are redirected to Login page
- JWT token stored in localStorage, sent with API requests

---

### Phase 2: Core Features

#### Goal 5: Session Management
Implement research session CRUD.

**Tasks:**
- Backend: Create `session_router.py` with all session endpoints
- Backend: Implement session store operations
- Frontend: Create session Pinia store
- Frontend: Add "New Research" button on Chat page
- Frontend: Create `HistoryPage.vue` with session list

**Acceptance Criteria:**
- User can create a new research session with a prompt
- User can see list of their sessions on History page
- User can click a session to view details
- User can delete a session

---

#### Goal 6: Chat Interface
Build the chat UI for user interaction.

**Tasks:**
- Backend: Create message endpoints in `session_router.py`
- Frontend: Create `ChatPage.vue` with full chat interface
- Frontend: Create `ChatInput.vue` component
- Frontend: Create `MessageList.vue` and `MessageBubble.vue`
- Frontend: Create chat Pinia store

**Acceptance Criteria:**
- User can type and send messages
- Messages appear in chat history
- Chat scrolls to latest message
- Loading indicator while waiting for response

---

#### Goal 7: Web Search Integration
Implement web search to gather sources.

**Tasks:**
- Backend: Create `search_service.py` with web search capability
- Backend: Parse search results into Source objects
- Backend: Store sources linked to session
- Backend: Create `source_router.py` endpoints
- Frontend: Create `SourceList.vue` and `SourceCard.vue`
- Frontend: Display sources in session detail

**Acceptance Criteria:**
- When user submits a research prompt, web search is triggered
- Sources are extracted and stored
- Source list shows title, URL, snippet, confidence
- Clicking source opens URL in new tab

---

#### Goal 8: Infographic Generation MVP
Generate basic infographics from research.

**Tasks:**
- Backend: Create `infographic_service.py` with template-based generation
- Backend: Create basic template (title, key points, sources)
- Backend: Generate PNG image and save to filesystem
- Backend: Create `infographic_router.py` endpoints
- Frontend: Create `InfographicViewer.vue` component
- Frontend: Display infographic in session detail

**Acceptance Criteria:**
- After sources are gathered, infographic is auto-generated
- Infographic shows title (from prompt), key bullet points, source count
- PNG image displays in session detail page
- Image path stored in database

---

### Phase 3: Polish & Export

#### Goal 9: History Filtering
Add filtering and search to history.

**Tasks:**
- Backend: Add query params to list sessions (date range, search)
- Frontend: Add date picker and search input to History page
- Frontend: Add pagination

**Acceptance Criteria:**
- User can filter sessions by date range
- User can search sessions by prompt text
- Pagination works for large session lists

---

#### Goal 10: Export Functionality
Allow exporting infographics and session data.

**Tasks:**
- Backend: Add export endpoint returning JSON or ZIP
- Backend: Support PNG and SVG export for infographic
- Frontend: Create `InfographicExport.vue` with download buttons
- Frontend: Add export buttons to session detail

**Acceptance Criteria:**
- User can download infographic as PNG
- User can download infographic as SVG
- User can download session data as JSON
- ZIP option includes infographic + sources + metadata

---

#### Goal 11: Advanced Infographic Templates
Add multiple template options with charts.

**Tasks:**
- Backend: Add template selection to infographic generation
- Backend: Implement "stats" template with bar/pie charts
- Backend: Implement "timeline" template
- Frontend: Add template selector in session detail
- Frontend: Regenerate infographic with new template

**Acceptance Criteria:**
- User can choose from 3 templates: basic, stats, timeline
- Stats template includes at least one chart
- Timeline template shows chronological info
- Regenerate button creates new infographic

---

## Non-Functional Requirements

### Security
- JWT tokens expire after 24 hours
- API endpoints validate JWT on every request
- Google OAuth client ID stored in environment variable
- No secrets committed to repository

### Performance
- API responses under 500ms for CRUD operations
- Infographic generation under 30 seconds
- Frontend initial load under 2 seconds

### Accessibility
- All interactive elements keyboard accessible
- ARIA labels on buttons and inputs
- Color contrast meets WCAG AA

### Internationalization
- All UI strings in i18n files
- Support English, Japanese, Chinese
- Date/time formatted per locale

---

## Environment Variables

### Backend (.env)
```
GOOGLE_CLIENT_ID=your-google-client-id
JWT_SECRET=your-jwt-secret
DATABASE_PATH=/workspace/data/duckdb
INFOGRAPHIC_PATH=/workspace/data/infographics
LOG_LEVEL=info
```

### Frontend (.env)
```
VITE_API_BASE=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_FRONTEND_PORT=3001
```

---

## Testing Strategy

### Backend Tests (pytest)
- Unit tests for each store (CRUD operations)
- Unit tests for each service (auth, search, infographic)
- Integration tests for each router endpoint
- Run: `pytest tests/ -v`

### Frontend Tests
- Component tests for key components
- E2E smoke test for login flow
- Run: `yarn test`

---

## Success Criteria

The project is complete when:
1. All 11 goals are implemented and tested
2. User can sign in, create research, view infographic, and export
3. All pytest tests pass
4. Frontend builds without errors
5. README documents all features and setup instructions


## Requirements

- [ ] Tasks:**
- [ ] Initialize Python package structure under `backend/src/infograph/`
- [ ] Create `main.py` with Click CLI for starting server
- [ ] Create `api_service.py` with FastAPI app, CORS middleware
- [ ] Create `health_router.py` with `/api/v1/health` endpoint
- [ ] Add `pyproject.toml` with dependencies
- [ ] Acceptance Criteria:**
- [ ] `python -m infograph.svc.main --port 8000` starts the server
- [ ] `GET http://localhost:8000/api/v1/health` returns `{"status": "ok"}`
- [ ] pytest test passes for health endpoint
- [ ] Tasks:**
- [ ] Initialize Vite + Vue 3 project
- [ ] Configure TailwindCSS and Element Plus
- [ ] Create router with placeholder pages (Login, Chat, History)
- [ ] Create `request.js` Axios instance pointing to backend
- [ ] Create health check API call on app load
- [ ] Acceptance Criteria:**
- [ ] `yarn dev` starts frontend on port 3001
- [ ] App shows "Backend Connected" status on successful health check
- [ ] Router navigates between placeholder pages
- [ ] Tasks:**
- [ ] Create abstract store interfaces for User, Session, Source, Infographic, Message
- [ ] Implement DuckDB stores following `DuckDBClient` patterns
- [ ] Create tables with proper schemas
- [ ] Write pytest tests for CRUD operations
- [ ] Acceptance Criteria:**
- [ ] Can create, read, update, delete all entity types
- [ ] All store tests pass
- [ ] Tables created automatically on first use
- [ ] Tasks:**
- [ ] Backend: Create `auth_service.py` to verify Google tokens
- [ ] Backend: Create `auth_router.py` with `/auth/google` and `/auth/me` endpoints
- [ ] Backend: Generate JWT tokens for authenticated sessions
- [ ] Frontend: Create `LoginPage.vue` with Google Sign-In button
- [ ] Frontend: Create `useAuth.js` composable for auth state
- [ ] Frontend: Create `auth` Pinia store
- [ ] Frontend: Add auth guard to router
- [ ] Acceptance Criteria:**
- [ ] User can click "Sign in with Google" button
- [ ] After Google auth, user is redirected to Chat page
- [ ] User info (name, email) is displayed in header
- [ ] Unauthenticated users are redirected to Login page
- [ ] JWT token stored in localStorage, sent with API requests
- [ ] Tasks:**
- [ ] Backend: Create `session_router.py` with all session endpoints
- [ ] Backend: Implement session store operations
- [ ] Frontend: Create session Pinia store
- [ ] Frontend: Add "New Research" button on Chat page
- [ ] Frontend: Create `HistoryPage.vue` with session list
- [ ] Acceptance Criteria:**
- [ ] User can create a new research session with a prompt
- [ ] User can see list of their sessions on History page
- [ ] User can click a session to view details
- [ ] User can delete a session
- [ ] Tasks:**
- [ ] Backend: Create message endpoints in `session_router.py`
- [ ] Frontend: Create `ChatPage.vue` with full chat interface
- [ ] Frontend: Create `ChatInput.vue` component
- [ ] Frontend: Create `MessageList.vue` and `MessageBubble.vue`
- [ ] Frontend: Create chat Pinia store
- [ ] Acceptance Criteria:**
- [ ] User can type and send messages
- [ ] Messages appear in chat history
- [ ] Chat scrolls to latest message
- [ ] Loading indicator while waiting for response
- [ ] Tasks:**
- [ ] Backend: Create `search_service.py` with web search capability
- [ ] Backend: Parse search results into Source objects
- [ ] Backend: Store sources linked to session
- [ ] Backend: Create `source_router.py` endpoints
- [ ] Frontend: Create `SourceList.vue` and `SourceCard.vue`
- [ ] Frontend: Display sources in session detail
- [ ] Acceptance Criteria:**
- [ ] When user submits a research prompt, web search is triggered
- [ ] Sources are extracted and stored
- [ ] Source list shows title, URL, snippet, confidence
- [ ] Clicking source opens URL in new tab
- [ ] Tasks:**
- [ ] Backend: Create `infographic_service.py` with template-based generation
- [ ] Backend: Create basic template (title, key points, sources)
- [ ] Backend: Generate PNG image and save to filesystem
- [ ] Backend: Create `infographic_router.py` endpoints
- [ ] Frontend: Create `InfographicViewer.vue` component
- [ ] Frontend: Display infographic in session detail
- [ ] Acceptance Criteria:**
- [ ] After sources are gathered, infographic is auto-generated
- [ ] Infographic shows title (from prompt), key bullet points, source count
- [ ] PNG image displays in session detail page
- [ ] Image path stored in database
- [ ] Tasks:**
- [ ] Backend: Add query params to list sessions (date range, search)
- [ ] Frontend: Add date picker and search input to History page
- [ ] Frontend: Add pagination
- [ ] Acceptance Criteria:**
- [ ] User can filter sessions by date range
- [ ] User can search sessions by prompt text
- [ ] Pagination works for large session lists
- [ ] Tasks:**
- [ ] Backend: Add export endpoint returning JSON or ZIP
- [ ] Backend: Support PNG and SVG export for infographic
- [ ] Frontend: Create `InfographicExport.vue` with download buttons
- [ ] Frontend: Add export buttons to session detail
- [ ] Acceptance Criteria:**
- [ ] User can download infographic as PNG
- [ ] User can download infographic as SVG
- [ ] User can download session data as JSON
- [ ] ZIP option includes infographic + sources + metadata
- [ ] Tasks:**
- [ ] Backend: Add template selection to infographic generation
- [ ] Backend: Implement "stats" template with bar/pie charts
- [ ] Backend: Implement "timeline" template
- [ ] Frontend: Add template selector in session detail
- [ ] Frontend: Regenerate infographic with new template
- [ ] Acceptance Criteria:**
- [ ] User can choose from 3 templates: basic, stats, timeline
- [ ] Stats template includes at least one chart
- [ ] Timeline template shows chronological info
- [ ] Regenerate button creates new infographic
- [ ] JWT tokens expire after 24 hours
- [ ] API endpoints validate JWT on every request
- [ ] Google OAuth client ID stored in environment variable
- [ ] No secrets committed to repository
- [ ] API responses under 500ms for CRUD operations
- [ ] Infographic generation under 30 seconds
- [ ] Frontend initial load under 2 seconds
- [ ] All interactive elements keyboard accessible
- [ ] ARIA labels on buttons and inputs
- [ ] Color contrast meets WCAG AA
- [ ] All UI strings in i18n files
- [ ] Support English, Japanese, Chinese
- [ ] Date/time formatted per locale
- [ ] Unit tests for each store (CRUD operations)
- [ ] Unit tests for each service (auth, search, infographic)
- [ ] Integration tests for each router endpoint
- [ ] Run: `pytest tests/ -v`
- [ ] Component tests for key components
- [ ] E2E smoke test for login flow
- [ ] Run: `yarn test`
- [ ] All 11 goals are implemented and tested
- [ ] User can sign in, create research, view infographic, and export
- [ ] All pytest tests pass
- [ ] Frontend builds without errors
- [ ] README documents all features and setup instructions

## Acceptance Criteria

- [ ] All requirements implemented
- [ ] All features have unit tests
- [ ] README.md documents all features
- [ ] All tests pass
