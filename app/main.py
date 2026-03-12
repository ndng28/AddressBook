"""FastAPI application for AddressBook."""

from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from app.routers import auth, contacts


def check_database_connection() -> tuple[bool, str]:
    """Check if database is accessible.
    
    Returns:
        Tuple of (is_healthy, status_message)
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True, "connected"
    except Exception as e:
        return False, f"error: {str(e)}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AddressBook API",
    description="A FastAPI application for managing contacts",
    version="0.1.0",
    # Only use lifespan in production, not tests
    # Tables will be created by test fixtures
)

# Include routers
app.include_router(auth.router)
app.include_router(contacts.router)


@app.get("/")
def root():
    """Root endpoint returning API info."""
    return {"message": "Welcome to AddressBook API"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    """Readiness probe - checks if service can handle requests.
    
    Checks:
    - Database connectivity
    
    Returns 200 if all checks pass, 503 if any fail.
    """
    checks = {}
    all_healthy = True

    # Check database
    db_healthy, db_status = check_database_connection()
    checks["database"] = db_status
    if not db_healthy:
        all_healthy = False

    if all_healthy:
        return {"status": "ok", "checks": checks}
    return {"status": "unhealthy", "checks": checks}, 503


@app.get("/health/deep")
def health_deep():
    """Deep health check - checks all dependencies.
    
    Checks:
    - Database connectivity
    - (Add more checks as dependencies grow)
    
    Returns 200 if all checks pass, 503 if any fail.
    """
    checks = {}
    all_healthy = True

    # Check database
    db_healthy, db_status = check_database_connection()
    checks["database"] = db_status
    if not db_healthy:
        all_healthy = False

    # Add timestamp for debugging
    checks["checked_at"] = datetime.now(UTC).isoformat()

    if all_healthy:
        return {"status": "ok", "checks": checks}
    return {"status": "unhealthy", "checks": checks}, 503
