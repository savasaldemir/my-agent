"""Pytest configuration"""

import os
from pathlib import Path

import pytest
from starlette.testclient import TestClient


TEST_DB_PATH = Path(__file__).resolve().parents[1] / "test_my_agent.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["JWT_SECRET"] = "test-secret-key-with-safe-length-123456"

from ..app import create_app


@pytest.fixture
def app():
    """Create test app"""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    return create_app()


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_test_db():
    """Remove test database file after each test for isolation."""
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()