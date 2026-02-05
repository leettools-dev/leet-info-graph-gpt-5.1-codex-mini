"""Tests for the source listing endpoint."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import asyncio
import pytest

from infograph.core.schemas import ResearchSessionCreate, SourceCreate
from infograph.services.auth_service import AuthService, AuthSettings
from infograph.stores.duckdb.session_store_duckdb import SessionStoreDuckDB
from infograph.stores.duckdb.source_store_duckdb import SourceStoreDuckDB
from infograph.stores.duckdb.user_store_duckdb import UserStoreDuckDB
from infograph.svc.api.v1.routers.source_router import SourceRouter


@staticmethod

@pytest.fixture
async def source_context(duckdb_settings):
    """Prepare an API client with a user, session, and stored sources."""

    user_store = UserStoreDuckDB(duckdb_settings)
    session_store = SessionStoreDuckDB(duckdb_settings)
    source_store = SourceStoreDuckDB(duckdb_settings)
    settings = AuthSettings(jwt_secret="test-secret", google_client_id="test-client")

    def fake_token_verifier(credential: str, audience: str):
        assert credential == "valid-credential"
        assert audience == settings.google_client_id
        return {
            "email": "user@example.com",
            "name": "Test Researcher",
            "sub": "google-123",
        }

    auth_service = AuthService(
        user_store=user_store,
        token_verifier=fake_token_verifier,
        settings=settings,
    )

    router = SourceRouter(
        session_store=session_store,
        source_store=source_store,
        auth_service=auth_service,
        user_store=user_store,
    )

    app = FastAPI()
    app.include_router(router, prefix="/api/v1/sessions")
    client = TestClient(app)

    _, token = await auth_service.authenticate("valid-credential")
    user = await user_store.get_by_google_id("google-123")
    session = await session_store.create(ResearchSessionCreate(prompt="test"), user.user_id)

    for idx in range(2):
        await source_store.create(
            SourceCreate(
                session_id=session.session_id,
                title=f"Source {idx + 1}",
                url=f"https://example.com/source-{idx + 1}",
                snippet=f"Snippet {idx + 1}",
                confidence=0.5 + (idx * 0.1),
            )
        )

    return {
        "client": client,
        "token": token,
        "session_id": session.session_id,
    }


def test_list_sources_requires_authorization(source_context):
    client = source_context["client"]
    session_id = source_context["session_id"]

    response = client.get(f"/api/v1/sessions/{session_id}/sources")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing Authorization header"


def test_list_sources_returns_sources(source_context):
    client = source_context["client"]
    session_id = source_context["session_id"]
    token = source_context["token"]

    response = client.get(
        f"/api/v1/sessions/{session_id}/sources",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload, list)
    assert len(payload) == 2
    assert payload[0]["session_id"] == session_id
    assert payload[0]["confidence"] >= 0.5
