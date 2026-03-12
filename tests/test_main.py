"""Tests for the main FastAPI application."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    """Health check endpoint should return 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint_exists():
    """Root endpoint should exist and return API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "AddressBook API" in data["message"]


class TestHealthCheckEndpoints:
    """Tests for health check endpoints."""

    def test_basic_health_returns_ok(self):
        """Basic health check should return ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_ready_with_database(self):
        """Health ready should check database connectivity."""
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "checks" in data
        assert "database" in data["checks"]
        assert data["checks"]["database"] == "connected"

    def test_health_deep_checks_all_dependencies(self):
        """Health deep should check all dependencies."""
        response = client.get("/health/deep")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "checks" in data
        assert "database" in data["checks"]
        assert "checked_at" in data["checks"]
