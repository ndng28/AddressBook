"""Tests for application configuration."""

import os

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_loads_from_env_vars():
    """Settings should load from environment variables."""
    # Set test environment variables
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DEBUG"] = "false"
    os.environ["ENVIRONMENT"] = "testing"
    
    settings = Settings()
    
    assert settings.database_url == "postgresql://test:test@localhost/test"
    assert settings.secret_key == "test-secret-key"
    assert settings.debug is False
    assert settings.environment == "testing"
    
    # Clean up
    del os.environ["DATABASE_URL"]
    del os.environ["SECRET_KEY"]
    del os.environ["DEBUG"]
    del os.environ["ENVIRONMENT"]


def test_settings_uses_defaults():
    """Settings should use sensible defaults."""
    # Make sure env vars are not set
    for var in ["DATABASE_URL", "SECRET_KEY", "DEBUG", "ENVIRONMENT"]:
        os.environ.pop(var, None)
    
    settings = Settings()
    
    # Check defaults
    assert settings.debug is True
    assert settings.environment == "development"
    assert settings.app_name == "AddressBook API"
    assert settings.app_version == "0.1.0"


def test_secret_key_is_required_in_production():
    """SECRET_KEY should be required in production environment."""
    os.environ["ENVIRONMENT"] = "production"
    os.environ.pop("SECRET_KEY", None)
    
    with pytest.raises(ValidationError):
        Settings()
    
    # Clean up
    del os.environ["ENVIRONMENT"]
