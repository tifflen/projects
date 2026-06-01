"""Unit tests for authentication module."""

import pytest
import jwt
from datetime import datetime, timedelta
from flask import Flask
from auth import generate_token, verify_token, token_required

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["JWT_SECRET_KEY"] = "test-jwt-secret"
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config["JWT_EXPIRATION_HOURS"] = 24
    return app

@pytest.fixture
def app_context(app):
    """Create app context for testing."""
    with app.app_context():
        yield app

def test_generate_token(app_context):
    """Test token generation."""
    token = generate_token("user123", "testuser")
    assert token
    assert isinstance(token, str)

def test_verify_token(app_context):
    """Test token verification."""
    token = generate_token("user123", "testuser")
    payload = verify_token(token)
    
    assert payload["user_id"] == "user123"
    assert payload["username"] == "testuser"

def test_verify_token_invalid(app_context):
    """Test verification of invalid token."""
    with pytest.raises(jwt.InvalidTokenError):
        verify_token("invalid-token")

def test_verify_token_expired(app_context):
    """Test verification of expired token."""
    with app_context.app_context():
        # Create an expired token
        payload = {
            "user_id": "user123",
            "username": "testuser",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() - timedelta(hours=1),
        }
        token = jwt.encode(
            payload,
            app_context.config["JWT_SECRET_KEY"],
            algorithm=app_context.config["JWT_ALGORITHM"],
        )
        
        with pytest.raises(jwt.ExpiredSignatureError):
            verify_token(token)

@pytest.fixture
def client(app):
    """Create test client."""
    @app.route("/protected")
    @token_required
    def protected():
        return {"status": "success"}
    
    return app.test_client()

def test_token_required_decorator_missing_token(client):
    """Test token_required decorator with missing token."""
    response = client.get("/protected")
    assert response.status_code == 401

def test_token_required_decorator_invalid_token(client):
    """Test token_required decorator with invalid token."""
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401

def test_token_required_decorator_valid_token(app, client):
    """Test token_required decorator with valid token."""
    with app.app_context():
        token = generate_token("user123", "testuser")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200