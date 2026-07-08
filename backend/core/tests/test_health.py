"""Health check tests"""

import pytest
from fastapi.testclient import TestClient
from ..app import create_app


@pytest.fixture
def client():
    """Test client"""
    app = create_app()
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check(client):
    """Test readiness check endpoint"""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
