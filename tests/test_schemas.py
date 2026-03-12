"""Tests for Pydantic schemas."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.schemas.user import UserCreate, UserLogin, UserResponse


class TestUserSchemas:
    """Test user-related Pydantic schemas."""

    def test_user_create_valid(self):
        """Should accept valid user creation data."""
        data = {
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User",
        }
        user = UserCreate(**data)
        assert user.email == "test@example.com"
        assert user.password == "securepassword123"
        assert user.full_name == "Test User"

    def test_user_create_requires_email(self):
        """Should require email field."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(password="password123")
        assert "email" in str(exc_info.value)

    def test_user_create_requires_password(self):
        """Should require password field."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com")
        assert "password" in str(exc_info.value)

    def test_user_create_validates_email_format(self):
        """Should validate email format."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid-email", password="password123")
        assert "email" in str(exc_info.value)

    def test_user_create_password_min_length(self):
        """Should enforce minimum password length."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="short")
        assert "password" in str(exc_info.value)

    def test_user_login_valid(self):
        """Should accept valid login credentials."""
        data = {
            "email": "test@example.com",
            "password": "password123",
        }
        login = UserLogin(**data)
        assert login.email == "test@example.com"
        assert login.password == "password123"

    def test_user_response_valid(self):
        """Should create valid user response."""
        now = datetime.now(UTC)
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        response = UserResponse(**data)
        assert response.email == "test@example.com"
        assert "password" not in response.model_dump()


class TestContactSchemas:
    """Test contact-related Pydantic schemas."""

    def test_contact_create_valid(self):
        """Should accept valid contact creation data."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "emails": [
                {"email": "john@example.com", "type": "work", "is_primary": True}
            ],
            "phones": [{"number": "+1234567890", "type": "mobile", "is_primary": True}],
            "company": "Acme Inc",
            "job_title": "Developer",
            "tags": ["work", "engineering"],
        }
        contact = ContactCreate(**data)
        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
        assert len(contact.emails) == 1
        assert len(contact.phones) == 1

    def test_contact_create_minimal(self):
        """Should accept minimal contact data (name only)."""
        data = {"first_name": "Jane"}
        contact = ContactCreate(**data)
        assert contact.first_name == "Jane"
        assert contact.last_name is None
        assert contact.emails == []

    def test_contact_create_validates_email_in_list(self):
        """Should validate email format within emails list."""
        data = {
            "first_name": "John",
            "emails": [{"email": "invalid-email", "type": "work"}],
        }
        with pytest.raises(ValidationError) as exc_info:
            ContactCreate(**data)
        assert "email" in str(exc_info.value)

    def test_contact_update_allows_partial(self):
        """Should allow partial updates."""
        data = {"first_name": "Updated Name"}
        update = ContactUpdate(**data)
        assert update.first_name == "Updated Name"
        assert update.last_name is None  # Not provided

    def test_contact_response_valid(self):
        """Should create valid contact response."""
        now = datetime.now(UTC)
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "emails": [
                {"email": "john@example.com", "type": "work", "is_primary": True}
            ],
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        response = ContactResponse(**data)
        assert response.first_name == "John"
        assert response.full_name == "John Doe"
        assert response.is_active is True

    def test_contact_response_computes_full_name(self):
        """Should compute full_name from first and last name."""
        now = datetime.now(UTC)
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "first_name": "Jane",
            "last_name": "Smith",
            "created_at": now,
            "updated_at": now,
        }
        response = ContactResponse(**data)
        assert response.full_name == "Jane Smith"

    def test_contact_response_full_name_unknown(self):
        """Should return 'Unknown' when no name provided."""
        now = datetime.now(UTC)
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "created_at": now,
            "updated_at": now,
        }
        response = ContactResponse(**data)
        assert response.full_name == "Unknown"
