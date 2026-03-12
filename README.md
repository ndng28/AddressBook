# AddressBook

A practice FastAPI project for managing contacts. This repository serves as an example open-source project demonstrating modern Python development practices.

## Overview

AddressBook is a simple REST API built with FastAPI and SQLAlchemy for managing personal and professional contacts. It demonstrates:

- FastAPI with automatic OpenAPI documentation
- SQLAlchemy ORM with PostgreSQL
- Pydantic for data validation
- pytest for testing
- Modern Python tooling (black, ruff, mypy)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, SQLite works for development)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AddressBook.git
cd AddressBook

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### API Documentation

Once running, view interactive docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run single test
pytest tests/test_users.py::test_create_user

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Check code style
ruff check .

# Fix auto-fixable issues
ruff check . --fix

# Format code
black .

# Type check
mypy .

# Run all checks
ruff check . && black --check . && mypy . && pytest
```

## Project Structure

```
AddressBook/
├── app/                  # Main application
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── routers/         # API routes
│   └── services/        # Business logic
├── tests/               # Test suite
├── alembic/            # Database migrations
└── AGENTS.md           # Development guidelines
```

## Contributing

This is a practice project. Feel free to fork and experiment!

## License

MIT License - see [LICENSE](LICENSE) file for details.
