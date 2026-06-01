"""Integration tests for Flask API endpoints."""

import pytest
import json
from app import app as flask_app
from config import TestingConfig
from db import init_db
from auth import generate_token

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    flask_app.config.from_object(TestingConfig)
    
    with flask_app.app_context():
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def auth_token(app):
    """Generate valid auth token."""
    with app.app_context():
        return generate_token("test_user_123", "testuser")

class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_index(self, client):
        """Test / endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["service"] == "Voice-Activated Virtual Assistant"
        assert data["status"] == "ready"

    def test_health(self, client):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"

class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_get_token_success(self, client):
        """Test successful token generation."""
        payload = {
            "user_id": "user123",
            "username": "testuser"
        }
        response = client.post(
            "/api/v1/auth/token",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "token" in data
        assert "expires_in" in data

    def test_get_token_missing_fields(self, client):
        """Test token generation with missing fields."""
        payload = {"user_id": "user123"}
        response = client.post(
            "/api/v1/auth/token",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 400

class TestTranscriptEndpoints:
    """Test transcript-related endpoints."""

    def test_get_transcripts_without_auth(self, client):
        """Test getting transcripts without authentication."""
        response = client.get("/api/v1/transcripts")
        assert response.status_code == 401

    def test_get_transcripts_with_auth(self, client, auth_token):
        """Test getting transcripts with valid token."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/api/v1/transcripts", headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "transcripts" in data
        assert "pagination" in data

class TestErrorHandling:
    """Test error handling."""

    def test_404_not_found(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data