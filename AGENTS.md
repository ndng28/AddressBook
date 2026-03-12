# AI Agent Guide - AddressBook

**Last Updated**: 2026-03-12
**Tech Stack**: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL

## Quick Commands

### Development
```bash
# Start dev server
uvicorn app.main:app --reload --port 8000

# Interactive API docs
open http://localhost:8000/docs
```

### Testing
```bash
# Run all tests
pytest

# Run single test (REQUIRED: use this format)
pytest tests/test_users.py::test_create_user

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_contacts.py -v

# Run tests matching pattern
pytest -k "test_create"
```

### Lint & Format
```bash
# Check code style
ruff check .

# Fix auto-fixable issues
ruff check . --fix

# Format code
black .

# Type check
mypy .

# Run all checks (CI)
ruff check . && black --check . && mypy . && pytest
```

## Code Style Guidelines

### Imports (isort style)
```python
# 1. Standard library
import json
from datetime import datetime
from typing import Optional

# 2. Third-party
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# 3. Local modules
from app.database import get_db
from app.models import Contact
```

### Naming Conventions
- **Files**: `snake_case.py` (e.g., `contact_service.py`)
- **Classes**: `PascalCase` (e.g., `ContactCreate`, `UserResponse`)
- **Functions/Variables**: `snake_case` (e.g., `get_contact_by_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_CONTACTS_PER_USER`)
- **Private**: `_leading_underscore` for internal use

### Type Hints (REQUIRED)
```python
# Always use type hints
def get_contact(db: Session, contact_id: int) -> Optional[Contact]:
    return db.query(Contact).filter(Contact.id == contact_id).first()

# Use Pydantic models for API schemas
class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
```

### Error Handling
```python
# Use HTTPException for API errors
if not contact:
    raise HTTPException(status_code=404, detail="Contact not found")

# Use specific exception types
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email already registered"
)
```

### Database Patterns
```python
# Use dependency injection for DB sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route with DB dependency
@app.get("/contacts/{contact_id}")
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    return contact_service.get_contact(db, contact_id)
```

### Docstrings
```python
def create_contact(db: Session, contact: ContactCreate) -> Contact:
    """Create a new contact for the current user.
    
    Args:
        db: Database session
        contact: Contact creation data
        
    Returns:
        The created contact
        
    Raises:
        HTTPException: If email already exists
    """
```

## Project Structure

```
AddressBook/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Settings
│   ├── database.py          # DB connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── contact.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   └── contact.py
│   ├── routers/             # API routes
│   │   ├── __init__.py
│   │   └── contacts.py
│   └── services/            # Business logic
│       ├── __init__.py
│       └── contact_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_contacts.py
│   └── test_users.py
├── alembic/                 # DB migrations
├── pyproject.toml
└── AGENTS.md
```

## Testing Guidelines

### Fixtures (in conftest.py)
```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db():
    # Setup test database
    db = TestingSessionLocal()
    yield db
    db.close()
```

### Test Naming
```python
# Test files: test_*.py
# Test functions: test_*
# Test classes: Test*

def test_create_contact_success(client):
    """Should create contact with valid data."""
    response = client.post("/contacts/", json={"name": "John"})
    assert response.status_code == 201

def test_create_contact_invalid_email(client):
    """Should reject contact with invalid email."""
    response = client.post("/contacts/", json={"email": "invalid"})
    assert response.status_code == 422
```

## Dependencies

Install with:
```bash
pip install -r requirements.txt
# or
pip install -e ".[dev]"
```

**Core**: fastapi, uvicorn, sqlalchemy, pydantic, psycopg2-binary
**Dev**: pytest, pytest-cov, black, ruff, mypy, httpx

## Environment Setup

```bash
# Copy env template
cp .env.example .env

# Required variables
DATABASE_URL=postgresql://user:pass@localhost/addressbook
SECRET_KEY=your-secret-key
DEBUG=true
```

---

**Note for AI Agents**: Always run `pytest path/to/test.py::test_name` for single tests. Use `ruff check . --fix` before committing.
