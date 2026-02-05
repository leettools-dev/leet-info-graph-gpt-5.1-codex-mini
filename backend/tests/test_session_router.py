"""Tests for the session and message router."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from infograph.core.schemas import ResearchSessionCreate, MessageCreate
from infograph.services.auth_service import AuthService, AuthSettings
from infograph.stores.duckdb.message_store_duckdb import MessageStoreDuckDB
from infograph.stores.duckdb.session_store_duckdb import SessionStoreDuckDB
from infograph.stores.duckdb.user_store_duckdb import UserStoreDuckDB
from infograph.svc.api.v1.routers.session_router import SessionRouter


@pytest.fixture
async def session_client(duckdb_settings):
    user_store = UserStoreDuckDB(duckdb_settings)
    session_store = SessionStoreDuckDB(duckdb_settings)
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
        auth_service=auth_service,
    )

    app = FastAPI()
    app.include_router(router, prefix="/api/v1/sessions")
    client = TestClient(app)

    _, token = await auth_service.authenticate("valid-credential")

    return client, token


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_create_list_and_delete_session(session_client):
    client, token = session_client
    response = client.post(
        "/api/v1/sessions",
        json={"prompt": "Test prompt"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 201
    session_data = response.json()
    assert session_data["prompt"] == "Test prompt"

    session_id = session_data["session_id"]

    response = client.get(f"/api/v1/sessions/{session_id}", headers=_auth_headers(token))
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id

    response = client.get(
        "/api/v1/sessions",
        headers=_auth_headers(token),
        params={"limit": 5, "offset": 0},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.delete(f"/api/v1/sessions/{session_id}", headers=_auth_headers(token))
    assert response.status_code == 200
    assert response.json()["success"] is True

    response = client.get(f"/api/v1/sessions/{session_id}", headers=_auth_headers(token))
    assert response.status_code == 404


@pytest.mark.anyio
async def test_unauthenticated_request_is_rejected(session_client):
    client, _ = session_client
    response = client.get("/api/v1/sessions")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_message_endpoints(session_client):
    client, token = session_client
    auth_headers = _auth_headers(token)

    response = client.post(
        "/api/v1/sessions",
        json={"prompt": "Message session"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    message_payload = {
        "session_id": session_id,
        "role": "user",
        "content": "Hello research",
    }

    response = client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json=message_payload,
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["content"] == "Hello research"

    response = client.get(f"/api/v1/sessions/{session_id}/messages", headers=auth_headers)
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 1
    assert messages[0]["session_id"] == session_id

    message_payload["session_id"] = "mismatch"
    response = client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json=message_payload,
        headers=auth_headers,
    )
    assert response.status_code == 400
