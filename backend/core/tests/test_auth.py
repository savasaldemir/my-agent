"""Authentication tests"""

from uuid import uuid4


def _unique_username() -> str:
    return f"testuser_{uuid4().hex[:8]}"


def _unique_email() -> str:
    return f"test_{uuid4().hex[:8]}@example.com"

def test_register(client):
    """Test user registration"""
    username = _unique_username()
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": _unique_email(),
            "password": "securepassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == username

def test_register_duplicate_username(client):
    """Test registration with duplicate username"""
    username = _unique_username()

    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": _unique_email(),
            "password": "securepassword123",
        },
    )
    
    # Second registration with same username
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": _unique_email(),
            "password": "securepassword123",
        },
    )
    assert response.status_code == 400

def test_login(client):
    """Test user login"""
    username = _unique_username()

    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": _unique_email(),
            "password": "securepassword123",
        },
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": "securepassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_invalid_password(client):
    """Test login with invalid password"""
    username = _unique_username()

    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": _unique_email(),
            "password": "securepassword123",
        },
    )
    
    # Login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401

def test_get_me(client):
    """Test get current user"""
    username = _unique_username()

    # Register first
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": _unique_email(),
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
    assert response.json()["username"] == username
