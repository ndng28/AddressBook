"""Tests for contact service."""

import uuid

import pytest
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactUpdate
from app.services.contact_service import (
    create_contact,
    delete_contact,
    get_contact,
    get_contacts,
    restore_contact,
    update_contact,
)


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password="hashedpass",
        full_name="Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_contact(db_session: Session, test_user: User):
    """Create a test contact."""
    contact = Contact(
        user_id=test_user.id,
        first_name="John",
        last_name="Doe",
        emails=[{"email": "john@example.com", "type": "work", "is_primary": True}],
        phones=[{"number": "+1234567890", "type": "mobile", "is_primary": True}],
        company="Acme Inc",
        tags=["work"],
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    return contact


class TestCreateContact:
    """Test contact creation."""

    def test_create_contact_success(self, db_session: Session, test_user: User):
        """Should create contact with valid data."""
        contact_data = ContactCreate(
            first_name="Jane",
            last_name="Smith",
            emails=[
                {"email": "jane@example.com", "type": "personal", "is_primary": True}
            ],
        )

        contact = create_contact(db_session, contact_data, test_user.id)

        assert contact.id is not None
        assert contact.first_name == "Jane"
        assert contact.last_name == "Smith"
        assert contact.user_id == test_user.id
        assert len(contact.emails) == 1
        assert contact.emails[0]["email"] == "jane@example.com"
        assert contact.is_active is True

    def test_create_contact_minimal_data(self, db_session: Session, test_user: User):
        """Should create contact with minimal data."""
        contact_data = ContactCreate(first_name="Minimal")

        contact = create_contact(db_session, contact_data, test_user.id)

        assert contact.first_name == "Minimal"
        assert contact.last_name is None


class TestGetContact:
    """Test retrieving contacts."""

    def test_get_contact_success(
        self, db_session: Session, test_user: User, test_contact: Contact
    ):
        """Should retrieve contact by ID."""
        contact = get_contact(db_session, test_contact.id, test_user.id)

        assert contact is not None
        assert contact.id == test_contact.id
        assert contact.first_name == "John"

    def test_get_contact_not_found(self, db_session: Session, test_user: User):
        """Should return None for non-existent contact."""
        fake_id = uuid.uuid4()
        contact = get_contact(db_session, fake_id, test_user.id)

        assert contact is None

    def test_get_contact_wrong_user(self, db_session: Session, test_contact: Contact):
        """Should return None for contact owned by different user."""
        other_user_id = uuid.uuid4()
        contact = get_contact(db_session, test_contact.id, other_user_id)

        assert contact is None

    def test_get_contacts_list(
        self, db_session: Session, test_user: User, test_contact: Contact
    ):
        """Should list all contacts for user."""
        contacts, total = get_contacts(db_session, test_user.id)

        assert total == 1
        assert len(contacts) == 1
        assert contacts[0].id == test_contact.id

    def test_get_contacts_excludes_deleted(
        self, db_session: Session, test_user: User, test_contact: Contact
    ):
        """Should exclude soft-deleted contacts."""
        # Soft delete the contact
        test_contact.is_active = False
        db_session.commit()

        contacts, total = get_contacts(db_session, test_user.id)

        assert total == 0
        assert len(contacts) == 0

    def test_get_contacts_with_pagination(self, db_session: Session, test_user: User):
        """Should paginate results."""
        # Create multiple contacts
        for i in range(5):
            contact = Contact(
                user_id=test_user.id,
                first_name=f"Contact{i}",
            )
            db_session.add(contact)
        db_session.commit()

        contacts, total = get_contacts(db_session, test_user.id, skip=0, limit=3)

        assert total == 5
        assert len(contacts) == 3


class TestUpdateContact:
    """Test contact updates."""

    def test_update_contact_success(
        self, db_session: Session, test_user: User, test_contact: Contact
    ):
        """Should update contact with new data."""
        update_data = ContactUpdate(first_name="Updated", last_name="Name")

        updated = update_contact(db_session, test_contact.id, update_data, test_user.id)

        assert updated is not None
        assert updated.first_name == "Updated"
        assert updated.last_name == "Name"
        # Original data preserved
        assert updated.company == "Acme Inc"

    def test_update_contact_not_found(self, db_session: Session, test_user: User):
        """Should return None for non-existent contact."""
        fake_id = uuid.uuid4()
        update_data = ContactUpdate(first_name="Updated")

        result = update_contact(db_session, fake_id, update_data, test_user.id)

        assert result is None


class TestDeleteContact:
    """Test contact deletion (soft delete)."""

    def test_delete_contact_success(
        self, db_session: Session, test_user: User, test_contact: Contact
    ):
        """Should soft delete contact."""
        result = delete_contact(db_session, test_contact.id, test_user.id)

        assert result is True

        # Verify contact is soft deleted
        db_session.refresh(test_contact)
        assert test_contact.is_active is False

    def test_delete_contact_not_found(self, db_session: Session, test_user: User):
        """Should return False for non-existent contact."""
        fake_id = uuid.uuid4()
        result = delete_contact(db_session, fake_id, test_user.id)

        assert result is False

    def test_restore_contact_success(
        self, db_session: Session, test_user: User, test_contact: Contact
    ):
        """Should restore soft-deleted contact."""
        # First delete it
        test_contact.is_active = False
        db_session.commit()

        result = restore_contact(db_session, test_contact.id, test_user.id)

        assert result is True

        # Verify contact is restored
        db_session.refresh(test_contact)
        assert test_contact.is_active is True

    def test_restore_contact_not_found(self, db_session: Session, test_user: User):
        """Should return False for non-existent contact."""
        fake_id = uuid.uuid4()
        result = restore_contact(db_session, fake_id, test_user.id)

        assert result is False
