"""Tests for the authentication router."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from infograph.services.auth_service import AuthService, AuthSettings
from infograph.stores.duckdb.user_store_duckdb import UserStoreDuckDB
from infograph.svc.api.v1.routers.auth_router import AuthRouter


@pytest.fixture
def auth_client(duckdb_settings):
    user_store = UserStoreDuckDB(duckdb_settings)
    settings = AuthSettings(jwt_secret="test-secret", google_client_id="test-client")

    def fake_token_verifier(credential: str, audience: str) -> dict[str, str]:
        assert credential == "valid-credential"
        assert audience == settings.google_client_id
        return {
            "email": "user@example.com",
            "name": "Test User",
            "sub": "google-123",
        }

    auth_service = AuthService(
        user_store=user_store,
        token_verifier=fake_token_verifier,
        settings=settings,
    )

    router = AuthRouter(user_store=user_store, auth_service=auth_service)
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/auth")
    return TestClient(app)


def test_google_sign_in_creates_user_and_returns_token(auth_client):
    response = auth_client.post("/api/v1/auth/google", json={"credential": "valid-credential"})
    assert response.status_code == 200
    payload = response.json()
    assert "user" in payload
    assert payload["user"]["email"] == "user@example.com"
    assert payload["token"]


def test_get_current_user_requires_authorization(auth_client):
    response = auth_client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing Authorization header"


def test_get_current_user_returns_user(auth_client):
    signin = auth_client.post("/api/v1/auth/google", json={"credential": "valid-credential"}).json()
    token = signin["token"]
    response = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


def test_logout_returns_success(auth_client):
    response = auth_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"success": True}
