"""Pytest Configuration and Fixtures.

This module provides shared pytest fixtures and configuration for the Color Correction System tests.
Includes database setup/teardown, test client configuration, and mock objects.

Usage:
    pytest                          # Run all tests
    pytest -v                       # Verbose output
    pytest --cov=./ --cov-report=html  # With coverage
    pytest tests/test_auth.py       # Specific test file
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator
import tempfile

# Import application components
try:
    from main import app
    from models.database import Base
    from config import settings
except ImportError:
    # Handle import errors gracefully for documentation
    pass


# ============================================================================
# Database Configuration
# ============================================================================

@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Get test database URL.
    
    Uses in-memory SQLite for faster tests.
    Each test session gets a temporary database file.
    
    Returns:
        SQLite database URL for testing
    """
    # Create temporary file for test database
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    return f"sqlite:///{db_path}"


@pytest.fixture(scope="session")
def test_engine(test_database_url: str):
    """Create test database engine.
    
    Args:
        test_database_url: Test database URL
        
    Yields:
        SQLAlchemy engine for testing
    """
    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test.
    
    Yields:
        SQLAlchemy session for testing
        
    Yields:
        Clean database session for each test
    """
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        # Rollback any uncommitted changes
        session.rollback()
        session.close()


# ============================================================================
# FastAPI Test Client
# ============================================================================

@pytest.fixture
def client(db_session: Session) -> TestClient:
    """Create FastAPI test client with test database.
    
    Args:
        db_session: Test database session
        
    Returns:
        FastAPI test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    # Override database dependency
    try:
        from main import get_db
        app.dependency_overrides[get_db] = override_get_db
    except ImportError:
        pass
    
    return TestClient(app)


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture
def valid_user_data() -> dict:
    """Fixture for valid user registration data.
    
    Returns:
        Dictionary with user registration data
    """
    return {
        "email": "testuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    }


@pytest.fixture
def invalid_user_data() -> dict:
    """Fixture for invalid user registration data.
    
    Returns:
        Dictionary with invalid user data
    """
    return {
        "email": "invalid-email",  # Invalid email format
        "password": "weak",  # Too short
        "full_name": ""
    }


@pytest.fixture
def auth_token(client: TestClient, valid_user_data: dict) -> str:
    """Fixture to get JWT auth token.
    
    Args:
        client: FastAPI test client
        valid_user_data: Valid user data for registration
        
    Returns:
        JWT authentication token
    """
    # Register user
    response = client.post("/api/auth/register", json=valid_user_data)
    
    if response.status_code == 201:
        return response.json().get("access_token")
    
    # Fallback: try login if registration fails (user might exist)
    login_data = {
        "email": valid_user_data["email"],
        "password": valid_user_data["password"]
    }
    response = client.post(
        "/api/auth/login",
        data=login_data
    )
    
    return response.json().get("access_token", "")


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Fixture for authorization headers with JWT token.
    
    Args:
        auth_token: JWT authentication token
        
    Returns:
        Dictionary with authorization header
    """
    return {"Authorization": f"Bearer {auth_token}"}


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_image_file():
    """Fixture for sample image file for upload tests.
    
    Yields:
        BytesIO object containing sample image data
    """
    from io import BytesIO
    
    # Create minimal valid JPEG
    jpg_data = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c'
        b'\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c'
        b'\x1c $.\'\"\,#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01'
        b'\x00\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01'
        b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07'
        b'\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd4\xff\xd9'
    )
    
    return BytesIO(jpg_data)


@pytest.fixture
def sample_image_metadata() -> dict:
    """Fixture for sample image metadata.
    
    Returns:
        Dictionary with image metadata
    """
    return {
        "camera_model": "Canon EOS 5D Mark IV",
        "lens": "Canon EF 24-70mm f/2.8L II",
        "iso": 400,
        "shutter_speed": "1/125",
        "aperture": "f/2.8"
    }


# ============================================================================
# Markers Configuration
# ============================================================================

def pytest_configure(config):
    """Register custom pytest markers.
    
    Args:
        config: Pytest config object
    """
    config.addinivalue_line(
        "markers",
        "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers",
        "auth: mark test as authentication related"
    )


# ============================================================================
# Test Execution Hooks
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """Modify test collection.
    
    Args:
        config: Pytest config
        items: Collected test items
    """
    # Add markers based on test location
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "test_" in str(item.name):
            item.add_marker(pytest.mark.unit)
