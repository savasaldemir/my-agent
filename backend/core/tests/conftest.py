"""Pytest configuration"""

import pytest
from fastapi.testclient import TestClient
from ..app import create_app


@pytest.fixture
def app():
    """Create test app"""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)
