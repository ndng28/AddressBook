"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = Field(default="AddressBook API")
    app_version: str = Field(default="0.1.0")
    
    # Environment
    environment: Literal["development", "testing", "production"] = Field(
        default="development"
    )
    debug: bool = Field(default=True)
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    
    # Database
    database_url: str = Field(default="sqlite:///./addressbook.db")
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate that SECRET_KEY is set in production."""
        if info.data.get("environment") == "production" and v == "dev-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be set in production environment")
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
