"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models to ensure they're registered with SQLAlchemy
from app.database import Base, get_db
from app.main import app
from app.models.contact import Contact  # noqa: F401
from app.models.user import User  # noqa: F401

# Create test database in memory
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create a test client with overridden database dependency."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session for this test
    session = TestingSessionLocal()
    
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    session.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
