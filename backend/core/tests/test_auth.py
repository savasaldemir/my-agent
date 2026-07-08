"""Authentication tests"""

import pytest
from fastapi.testclient import TestClient
from ..app import create_app
from ..schemas import UserCreate

@pytest.fixture
def client():
    """Test client"""
    app = create_app()
    return TestClient(app)

def test_register(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testuser"

def test_register_duplicate_username(client):
    """Test registration with duplicate username"""
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test1@example.com",
            "password": "securepassword123",
        },
    )
    
    # Second registration with same username
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 400

def test_login(client):
    """Test user login"""
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_invalid_password(client):
    """Test login with invalid password"""
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    
    # Login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401

def test_get_me(client):
    """Test get current user"""
    # Register first
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    token = reg_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
