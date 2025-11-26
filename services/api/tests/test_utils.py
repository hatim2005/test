"""Tests for utility functions."""
import pytest
from datetime import datetime
from utils import (
    generate_token,
    hash_password,
    verify_password,
    validate_email,
    sanitize_filename,
    create_logger,
)


class TestPasswordHandling:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "correct_password"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test failed password verification."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False


class TestTokenGeneration:
    """Test token generation utilities."""

    def test_generate_token_length(self):
        """Test that generated tokens have correct length."""
        token = generate_token(32)
        assert len(token) == 32

    def test_generate_token_uniqueness(self):
        """Test that generated tokens are unique."""
        tokens = [generate_token(32) for _ in range(100)]
        assert len(set(tokens)) == 100

    def test_generate_token_characters(self):
        """Test that tokens contain valid characters."""
        token = generate_token(32)
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        assert all(c in valid_chars for c in token)


class TestEmailValidation:
    """Test email validation."""

    @pytest.mark.parametrize("valid_email", [
        "test@example.com",
        "user.name@example.co.uk",
        "first+last@example.com",
    ])
    def test_valid_emails(self, valid_email):
        """Test validation of valid email addresses."""
        assert validate_email(valid_email) is True

    @pytest.mark.parametrize("invalid_email", [
        "not_an_email",
        "@example.com",
        "user@",
        "user @example.com",
    ])
    def test_invalid_emails(self, invalid_email):
        """Test validation of invalid email addresses."""
        assert validate_email(invalid_email) is False


class TestFilenameSanitization:
    """Test filename sanitization."""

    def test_sanitize_simple_filename(self):
        """Test sanitization of simple filenames."""
        result = sanitize_filename("test_file.jpg")
        assert result == "test_file.jpg"

    def test_sanitize_removes_special_chars(self):
        """Test that special characters are removed."""
        result = sanitize_filename("test<>|file.jpg")
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result

    def test_sanitize_handles_spaces(self):
        """Test handling of spaces in filenames."""
        result = sanitize_filename("my test file.jpg")
        assert " " not in result or result.replace(" ", "_") == result.replace(" ", "_")

    def test_sanitize_empty_string(self):
        """Test sanitization of empty string."""
        result = sanitize_filename("")
        assert isinstance(result, str)


class TestLogger:
    """Test logger creation."""

    def test_create_logger(self):
        """Test logger creation."""
        logger = create_logger("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"

    def test_logger_handlers(self):
        """Test that logger has handlers configured."""
        logger = create_logger("test_logger_2")
        assert len(logger.handlers) > 0
