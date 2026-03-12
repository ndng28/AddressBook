"""Tests for authentication utilities."""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.config import get_settings
from app.utils.auth import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing utilities."""
    
    def test_hash_password_returns_string(self):
        """Should return hashed password string."""
        password = "mypassword123"
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should be different from plain text
    
    def test_verify_password_correct(self):
        """Should return True for correct password."""
        password = "mypassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Should return False for incorrect password."""
        password = "mypassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_password_different_each_time(self):
        """Should generate different hashes for same password."""
        password = "mypassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTToken:
    """Test JWT token creation and verification."""
    
    def test_create_access_token_returns_string(self):
        """Should return JWT token string."""
        settings = get_settings()
        token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(minutes=30),
        )
        
        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT has 3 parts
    
    def test_create_access_token_contains_data(self):
        """Should include subject in token payload."""
        settings = get_settings()
        token = create_access_token(
            data={"sub": "test@example.com", "user_id": "123"},
            expires_delta=timedelta(minutes=30),
        )
        
        # Decode without verification to check payload
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == "123"
    
    def test_create_access_token_has_expiration(self):
        """Should include expiration claim."""
        settings = get_settings()
        token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(minutes=30),
        )
        
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        assert "exp" in payload
        
        # Expiration should be in the future
        exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert exp_datetime > datetime.now(timezone.utc)
    
    def test_decode_token_valid(self):
        """Should decode valid token successfully."""
        settings = get_settings()
        token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(minutes=30),
        )
        
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
    
    def test_decode_token_invalid(self):
        """Should return None for invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = decode_token(invalid_token)
        assert payload is None
    
    def test_decode_token_expired(self):
        """Should return None for expired token."""
        settings = get_settings()
        # Create token that expired 1 hour ago
        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
        expired_token = jwt.encode(
            {"sub": "test@example.com", "exp": expired_time},
            settings.secret_key,
            algorithm="HS256",
        )
        
        payload = decode_token(expired_token)
        assert payload is None
    
    def test_decode_token_wrong_secret(self):
        """Should return None for token with wrong secret."""
        settings = get_settings()
        # Create token with wrong secret
        wrong_token = jwt.encode(
            {"sub": "test@example.com"},
            "wrong-secret",
            algorithm="HS256",
        )
        
        payload = decode_token(wrong_token)
        assert payload is None
