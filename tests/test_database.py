"""Tests for database configuration and models."""

import uuid
from datetime import datetime

import pytest

from app.database import get_db
from app.models.contact import Contact
from app.models.user import User


def test_user_model_creation(db_session):
    """Should create a user with all required fields."""
    user = User(
        email="test@example.com",
        hashed_password="hashedpassword123",
        full_name="Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_user_email_unique(db_session):
    """Should enforce unique email constraint."""
    user1 = User(email="unique@example.com", hashed_password="pass1")
    user2 = User(email="unique@example.com", hashed_password="pass2")

    db_session.add(user1)
    db_session.commit()

    db_session.add(user2)
    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()


def test_contact_model_creation(db_session):
    """Should create a contact with all fields."""
    # First create a user
    user = User(email="owner@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()

    contact = Contact(
        user_id=user.id,
        first_name="John",
        last_name="Doe",
        company="Acme Inc",
        job_title="Developer",
        emails=[{"email": "john@example.com", "type": "work", "is_primary": True}],
        phones=[{"number": "+1234567890", "type": "mobile", "is_primary": True}],
        tags=["work", "engineering"],
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    assert contact.id is not None
    assert isinstance(contact.id, uuid.UUID)
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.user_id == user.id
    assert contact.emails == [
        {"email": "john@example.com", "type": "work", "is_primary": True}
    ]
    assert contact.phones == [
        {"number": "+1234567890", "type": "mobile", "is_primary": True}
    ]
    assert contact.tags == ["work", "engineering"]
    assert contact.is_active is True


def test_contact_belongs_to_user(db_session):
    """Should link contact to its owner user."""
    user = User(email="owner@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()

    contact = Contact(user_id=user.id, first_name="Jane", last_name="Smith")
    db_session.add(contact)
    db_session.commit()

    # Access relationship
    assert contact.user.email == "owner@example.com"
    assert len(user.contacts) == 1
    assert user.contacts[0].first_name == "Jane"


def test_soft_delete_contact(db_session):
    """Should soft delete contact by setting is_active to False."""
    user = User(email="owner@example.com", hashed_password="pass")
    db_session.add(user)
    db_session.commit()

    contact = Contact(user_id=user.id, first_name="ToDelete")
    db_session.add(contact)
    db_session.commit()

    # Soft delete
    contact.is_active = False
    db_session.commit()
    db_session.refresh(contact)

    assert contact.is_active is False
    # Contact still exists in database
    assert (
        db_session.query(Contact).filter(Contact.id == contact.id).first() is not None
    )


def test_get_db_dependency():
    """Should yield a database session and close it properly."""
    db_gen = get_db()
    db = next(db_gen)

    assert db is not None

    # Should close on cleanup
    try:
        next(db_gen)
    except StopIteration:
        pass  # Expected
