"""Tests for the session router."""

from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from infograph.services.auth_service import AuthService, AuthSettings
from infograph.stores.duckdb.message_store_duckdb import MessageStoreDuckDB
from infograph.stores.duckdb.session_store_duckdb import SessionStoreDuckDB
from infograph.stores.duckdb.source_store_duckdb import SourceStoreDuckDB
from infograph.stores.duckdb.user_store_duckdb import UserStoreDuckDB
from infograph.svc.api.v1.routers.session_router import SessionRouter


class FakeSearchService:
    """No-op search service used in tests."""

    async def gather_sources(self, session_id: str, prompt: str) -> list[dict]:
        return []


async def _build_session_context(duckdb_settings):
    user_store = UserStoreDuckDB(duckdb_settings)
    session_store = SessionStoreDuckDB(duckdb_settings)
    source_store = SourceStoreDuckDB(duckdb_settings)
    message_store = MessageStoreDuckDB(duckdb_settings)
    settings = AuthSettings(jwt_secret="test-secret", google_client_id="test-client")

    def fake_token_verifier(credential: str, audience: str) -> dict[str, str]:
        assert credential == "valid-credential"
        assert audience == settings.google_client_id
        return {
            "email": "user@example.com",
            "name": "Researcher",
            "sub": "google-123",
        }

    auth_service = AuthService(
        user_store=user_store,
        token_verifier=fake_token_verifier,
        settings=settings,
    )

    router = SessionRouter(
        session_store=session_store,
        message_store=message_store,
        source_store=source_store,
        user_store=user_store,
        auth_service=auth_service,
        search_service=FakeSearchService(),
    )

    app = FastAPI()
    app.include_router(router, prefix="/api/v1/sessions")
    client = TestClient(app)

    _, token = await auth_service.authenticate("valid-credential")

    return {
        "client": client,
        "token": token,
    }


@pytest.fixture
def session_context(duckdb_settings):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_build_session_context(duckdb_settings))
    finally:
        loop.close()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_create_session_requires_authorization(session_context):
    client = session_context["client"]

    response = client.post("/api/v1/sessions", json={"prompt": "AI research"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing Authorization header"


def test_create_session_returns_session(session_context):
    client = session_context["client"]
    token = session_context["token"]

    response = client.post(
        "/api/v1/sessions",
        json={"prompt": "Future of science"},
        headers=_auth_headers(token),
    )

    assert response.status_code == 201
    payload = response.json()

    assert payload["prompt"] == "Future of science"
    assert payload["status"] == "pending"
    assert payload["session_id"]


def test_list_sessions_returns_user_sessions(session_context):
    client = session_context["client"]
    token = session_context["token"]

    client.post(
        "/api/v1/sessions",
        json={"prompt": "Electric vehicles"},
        headers=_auth_headers(token),
    )

    response = client.get("/api/v1/sessions", headers=_auth_headers(token))

    assert response.status_code == 200
    sessions = response.json()

    assert isinstance(sessions, list)
    assert len(sessions) == 1
    assert sessions[0]["prompt"] == "Electric vehicles"


def test_get_session_returns_session(session_context):
    client = session_context["client"]
    token = session_context["token"]

    create_response = client.post(
        "/api/v1/sessions",
        json={"prompt": "Quantum computing"},
        headers=_auth_headers(token),
    )
    session = create_response.json()

    response = client.get(
        f"/api/v1/sessions/{session['session_id']}",
        headers=_auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["session_id"] == session["session_id"]


def test_delete_session_removes_session(session_context):
    client = session_context["client"]
    token = session_context["token"]

    create_response = client.post(
        "/api/v1/sessions",
        json={"prompt": "Space exploration"},
        headers=_auth_headers(token),
    )
    session = create_response.json()

    delete_response = client.delete(
        f"/api/v1/sessions/{session['session_id']}",
        headers=_auth_headers(token),
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {"success": True}

    get_response = client.get(
        f"/api/v1/sessions/{session['session_id']}",
        headers=_auth_headers(token),
    )

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Session not found"
