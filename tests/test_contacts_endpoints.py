"""Tests for contact API endpoints."""

import uuid
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.contact import Contact
from app.models.user import User
from app.utils.auth import create_access_token, get_password_hash


@pytest.fixture
def client_with_db():
    """Create a test client with database session accessible."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    # Create test database in memory with static pool to share connection
    TEST_DATABASE_URL = "sqlite://"
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create a connection that will be shared
    connection = engine.connect()

    # Bind the session to the connection
    session = TestingSessionLocal(bind=connection)

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client, session

    # Cleanup
    session.close()
    connection.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_and_auth(client_with_db):
    """Create a test user and return auth headers."""
    client, db = client_with_db

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=timedelta(minutes=30),
    )
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    return client, db, user, auth_headers


@pytest.fixture
def other_user_and_auth(client_with_db):
    """Create another test user for access control tests."""
    client, db = client_with_db

    user = User(
        email="other@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Other User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=timedelta(minutes=30),
    )
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    return client, db, user, auth_headers


@pytest.fixture
def test_contact(test_user_and_auth):
    """Create a test contact."""
    client, db, user, auth_headers = test_user_and_auth

    contact = Contact(
        user_id=user.id,
        first_name="John",
        last_name="Doe",
        emails=[{"email": "john@example.com", "type": "work", "is_primary": True}],
        phones=[{"number": "+1234567890", "type": "mobile", "is_primary": True}],
        company="Acme Inc",
        tags=["work"],
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return client, db, user, auth_headers, contact


class TestCreateContact:
    """Test POST /api/v1/contacts"""

    def test_create_contact_success(self, test_user_and_auth):
        """Should create contact with valid data."""
        client, db, user, auth_headers = test_user_and_auth

        contact_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "emails": [{"email": "jane@example.com", "type": "personal", "is_primary": True}],
            "phones": [{"number": "+9876543210", "type": "mobile", "is_primary": True}],
            "company": "Tech Corp",
            "job_title": "Engineer",
            "tags": ["personal", "tech"],
        }

        response = client.post("/api/v1/contacts", json=contact_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert data["full_name"] == "Jane Smith"
        assert len(data["emails"]) == 1
        assert data["emails"][0]["email"] == "jane@example.com"
        assert data["company"] == "Tech Corp"
        assert data["is_active"] is True
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data

    def test_create_contact_minimal_data(self, test_user_and_auth):
        """Should create contact with minimal data."""
        client, db, user, auth_headers = test_user_and_auth

        contact_data = {"first_name": "Minimal"}

        response = client.post("/api/v1/contacts", json=contact_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Minimal"
        assert data["full_name"] == "Minimal"

    def test_create_contact_invalid_email_format(self, test_user_and_auth):
        """Should reject contact with invalid email format."""
        client, db, user, auth_headers = test_user_and_auth

        contact_data = {
            "first_name": "Test",
            "emails": [{"email": "invalid-email", "type": "work"}],
        }

        response = client.post("/api/v1/contacts", json=contact_data, headers=auth_headers)

        assert response.status_code == 422

    def test_create_contact_invalid_phone_type(self, test_user_and_auth):
        """Should reject contact with invalid phone type."""
        client, db, user, auth_headers = test_user_and_auth

        contact_data = {
            "first_name": "Test",
            "phones": [{"number": "+1234567890", "type": "invalid_type"}],
        }

        response = client.post("/api/v1/contacts", json=contact_data, headers=auth_headers)

        assert response.status_code == 422

    def test_create_contact_unauthorized(self, client_with_db):
        """Should reject request without authentication."""
        client, db = client_with_db
        contact_data = {"first_name": "Test"}

        response = client.post("/api/v1/contacts", json=contact_data)

        assert response.status_code == 401


class TestListContacts:
    """Test GET /api/v1/contacts"""

    def test_list_contacts_success(self, test_contact):
        """Should list contacts for authenticated user."""
        client, db, user, auth_headers, contact = test_contact

        response = client.get("/api/v1/contacts", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"]
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == str(contact.id)
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["pages"] == 1

    def test_list_contacts_pagination(self, test_user_and_auth):
        """Should paginate contact list."""
        client, db, user, auth_headers = test_user_and_auth

        # Create additional contacts
        for i in range(5):
            contact = Contact(
                user_id=user.id,
                first_name=f"Contact{i}",
            )
            db.add(contact)
        db.commit()

        response = client.get("/api/v1/contacts?skip=0&limit=3", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5
        assert data["pages"] == 2

    def test_list_contacts_empty(self, test_user_and_auth):
        """Should return empty list when no contacts."""
        client, db, user, auth_headers = test_user_and_auth

        response = client.get("/api/v1/contacts", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_contacts_unauthorized(self, client_with_db):
        """Should reject request without authentication."""
        client, db = client_with_db

        response = client.get("/api/v1/contacts")

        assert response.status_code == 401

    def test_list_contacts_excludes_deleted(self, test_contact):
        """Should not include soft-deleted contacts."""
        client, db, user, auth_headers, contact = test_contact

        # Soft delete the contact
        contact.is_active = False
        db.commit()

        response = client.get("/api/v1/contacts", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0


class TestGetContact:
    """Test GET /api/v1/contacts/{id}"""

    def test_get_contact_success(self, test_contact):
        """Should get contact details."""
        client, db, user, auth_headers, contact = test_contact

        response = client.get(f"/api/v1/contacts/{contact.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(contact.id)
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["full_name"] == "John Doe"
        assert data["company"] == "Acme Inc"

    def test_get_contact_not_found(self, test_user_and_auth):
        """Should return 404 for non-existent contact."""
        client, db, user, auth_headers = test_user_and_auth

        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/contacts/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_get_contact_wrong_user(self, test_contact, other_user_and_auth):
        """Should return 403 when accessing other user's contact."""
        client, db, user, auth_headers, contact = test_contact
        other_client, other_db, other_user, other_auth_headers = other_user_and_auth

        response = other_client.get(f"/api/v1/contacts/{contact.id}", headers=other_auth_headers)

        assert response.status_code == 403

    def test_get_contact_unauthorized(self, client_with_db, test_contact):
        """Should reject request without authentication."""
        client, db, user, auth_headers, contact = test_contact

        response = client.get(f"/api/v1/contacts/{contact.id}")

        assert response.status_code == 401


class TestUpdateContact:
    """Test PATCH /api/v1/contacts/{id}"""

    def test_update_contact_success(self, test_contact):
        """Should update contact with valid data."""
        client, db, user, auth_headers, contact = test_contact

        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "company": "New Company",
        }

        response = client.patch(f"/api/v1/contacts/{contact.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["full_name"] == "Updated Name"
        assert data["company"] == "New Company"
        # Original data preserved
        assert len(data["emails"]) == 1

    def test_update_contact_not_found(self, test_user_and_auth):
        """Should return 404 for non-existent contact."""
        client, db, user, auth_headers = test_user_and_auth

        fake_id = uuid.uuid4()
        update_data = {"first_name": "Updated"}

        response = client.patch(f"/api/v1/contacts/{fake_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 404

    def test_update_contact_wrong_user(self, test_contact, other_user_and_auth):
        """Should return 403 when updating other user's contact."""
        client, db, user, auth_headers, contact = test_contact
        other_client, other_db, other_user, other_auth_headers = other_user_and_auth

        update_data = {"first_name": "Hacked"}

        response = other_client.patch(f"/api/v1/contacts/{contact.id}", json=update_data, headers=other_auth_headers)

        assert response.status_code == 403

    def test_update_contact_unauthorized(self, client_with_db, test_contact):
        """Should reject request without authentication."""
        client, db, user, auth_headers, contact = test_contact

        update_data = {"first_name": "Updated"}
        response = client.patch(f"/api/v1/contacts/{contact.id}", json=update_data)

        assert response.status_code == 401


class TestDeleteContact:
    """Test DELETE /api/v1/contacts/{id}"""

    def test_delete_contact_success(self, test_contact):
        """Should soft delete contact."""
        client, db, user, auth_headers, contact = test_contact

        response = client.delete(f"/api/v1/contacts/{contact.id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify soft delete in database
        db.refresh(contact)
        assert contact.is_active is False

    def test_delete_contact_not_found(self, test_user_and_auth):
        """Should return 404 for non-existent contact."""
        client, db, user, auth_headers = test_user_and_auth

        fake_id = uuid.uuid4()
        response = client.delete(f"/api/v1/contacts/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_contact_wrong_user(self, test_contact, other_user_and_auth):
        """Should return 403 when deleting other user's contact."""
        client, db, user, auth_headers, contact = test_contact
        other_client, other_db, other_user, other_auth_headers = other_user_and_auth

        response = other_client.delete(f"/api/v1/contacts/{contact.id}", headers=other_auth_headers)

        assert response.status_code == 403

    def test_delete_contact_unauthorized(self, client_with_db, test_contact):
        """Should reject request without authentication."""
        client, db, user, auth_headers, contact = test_contact

        response = client.delete(f"/api/v1/contacts/{contact.id}")

        assert response.status_code == 401


class TestListDeletedContacts:
    """Test GET /api/v1/contacts/deleted"""

    def test_list_deleted_contacts(self, test_contact):
        """Should list soft-deleted contacts."""
        client, db, user, auth_headers, contact = test_contact

        # Soft delete the contact
        contact.is_active = False
        db.commit()

        response = client.get("/api/v1/contacts/deleted", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == str(contact.id)
        assert data["total"] == 1

    def test_list_deleted_contacts_empty(self, test_user_and_auth):
        """Should return empty list when no deleted contacts."""
        client, db, user, auth_headers = test_user_and_auth

        response = client.get("/api/v1/contacts/deleted", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_deleted_contacts_unauthorized(self, client_with_db):
        """Should reject request without authentication."""
        client, db = client_with_db

        response = client.get("/api/v1/contacts/deleted")

        assert response.status_code == 401


class TestRestoreContact:
    """Test POST /api/v1/contacts/{id}/restore"""

    def test_restore_contact_success(self, test_contact):
        """Should restore soft-deleted contact."""
        client, db, user, auth_headers, contact = test_contact

        # First soft delete the contact
        contact.is_active = False
        db.commit()

        response = client.post(f"/api/v1/contacts/{contact.id}/restore", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(contact.id)
        assert data["is_active"] is True

        # Verify in database
        db.refresh(contact)
        assert contact.is_active is True

    def test_restore_contact_not_found(self, test_user_and_auth):
        """Should return 404 for non-existent contact."""
        client, db, user, auth_headers = test_user_and_auth

        fake_id = uuid.uuid4()
        response = client.post(f"/api/v1/contacts/{fake_id}/restore", headers=auth_headers)

        assert response.status_code == 404

    def test_restore_contact_wrong_user(self, test_contact, other_user_and_auth):
        """Should return 403 when restoring other user's contact."""
        client, db, user, auth_headers, contact = test_contact
        other_client, other_db, other_user, other_auth_headers = other_user_and_auth

        # First soft delete the contact
        contact.is_active = False
        db.commit()

        response = other_client.post(f"/api/v1/contacts/{contact.id}/restore", headers=other_auth_headers)

        assert response.status_code == 403

    def test_restore_contact_unauthorized(self, client_with_db, test_contact):
        """Should reject request without authentication."""
        client, db, user, auth_headers, contact = test_contact

        response = client.post(f"/api/v1/contacts/{contact.id}/restore")

        assert response.status_code == 401
