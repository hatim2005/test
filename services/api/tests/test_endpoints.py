"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from conftest import client, test_db


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_user_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "secure_password_123",
            },
        )
        assert response.status_code == 201
        assert response.json()["email"] == "newuser@example.com"

    def test_register_duplicate_email(self, client):
        """Test that duplicate email registration fails."""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser1",
                "password": "password",
            },
        )
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser2",
                "password": "password",
            },
        )
        assert response.status_code == 400

    def test_login_success(self, client):
        """Test successful login."""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "password123",
            },
        )
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_invalid_password(self, client):
        """Test login with invalid password."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "wrong_password"},
        )
        assert response.status_code == 401


class TestImageEndpoints:
    """Test image upload and retrieval endpoints."""

    def test_upload_image_unauthorized(self, client):
        """Test that image upload requires authentication."""
        response = client.post(
            "/api/v1/images/upload",
            files={"file": ("test.jpg", b"fake image data")},
        )
        assert response.status_code == 401

    def test_get_images_list(self, client, token):
        """Test retrieving list of images."""
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/images", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_image_by_id(self, client, token):
        """Test retrieving specific image."""
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/images/1", headers=headers)
        assert response.status_code in [200, 404]


class TestDetectionEndpoints:
    """Test ArUco marker detection endpoints."""

    def test_detect_markers_no_auth(self, client):
        """Test marker detection requires authentication."""
        response = client.post(
            "/api/v1/detection/detect",
            json={"image_id": 1},
        )
        assert response.status_code == 401

    def test_detect_markers_invalid_image(self, client, token):
        """Test detection with invalid image ID."""
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/v1/detection/detect",
            json={"image_id": 99999},
            headers=headers,
        )
        assert response.status_code == 404


class TestCorrectionEndpoints:
    """Test color correction endpoints."""

    def test_apply_correction_unauthorized(self, client):
        """Test correction requires authentication."""
        response = client.post(
            "/api/v1/correction/apply",
            json={"image_id": 1, "method": "auto_balance"},
        )
        assert response.status_code == 401

    def test_get_correction_methods(self, client):
        """Test retrieving available correction methods."""
        response = client.get("/api/v1/correction/methods")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestHealthCheck:
    """Test API health check endpoints."""

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_readiness_endpoint(self, client):
        """Test readiness endpoint."""
        response = client.get("/ready")
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling and responses."""

    def test_invalid_endpoint(self, client):
        """Test 404 for invalid endpoint."""
        response = client.get("/api/v1/invalid")
        assert response.status_code == 404

    def test_malformed_json(self, client):
        """Test 400 for malformed JSON."""
        response = client.post(
            "/api/v1/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422
