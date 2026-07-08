"""CRUD endpoint tests"""

import pytest
from fastapi.testclient import TestClient
from ..app import create_app

@pytest.fixture
def client():
    """Test client"""
    app = create_app()
    return TestClient(app)

@pytest.fixture
def auth_token(client):
    """Get authentication token"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    return response.json()["access_token"]

# ==================== PROJECT TESTS ====================

def test_create_project(client, auth_token):
    """Test project creation"""
    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Test Project",
            "language": "python",
            "description": "A test project",
            "repository_url": "https://github.com/test/project",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Project"

def test_list_projects(client, auth_token):
    """Test project listing"""
    # Create project first
    client.post(
        "/api/v1/projects/",
        json={
            "name": "Test Project",
            "language": "python",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    response = client.get(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_project(client, auth_token):
    """Test get project"""
    # Create project first
    create_response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Test Project",
            "language": "python",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    project_id = create_response.json()["id"]
    
    response = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == project_id

def test_update_project(client, auth_token):
    """Test project update"""
    # Create project first
    create_response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Test Project",
            "language": "python",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    project_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated Project"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project"

def test_delete_project(client, auth_token):
    """Test project deletion"""
    # Create project first
    create_response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Test Project",
            "language": "python",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    project_id = create_response.json()["id"]
    
    response = client.delete(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 204

# ==================== SESSION TESTS ====================

def test_create_session(client, auth_token):
    """Test session creation"""
    # Create project first
    project_response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Test Project",
            "language": "python",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    project_id = project_response.json()["id"]
    
    response = client.post(
        "/api/v1/sessions/",
        json={
            "project_id": project_id,
            "session_type": "analyze",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    assert response.json()["session_type"] == "analyze"

def test_list_sessions(client, auth_token):
    """Test session listing"""
    response = client.get(
        "/api/v1/sessions/",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
