"""Tests for the health router."""

from fastapi.testclient import TestClient

from infograph.svc.api_service import create_app


client = TestClient(create_app())


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}
