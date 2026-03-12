"""FastAPI application for AddressBook."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth


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


@app.get("/")
def root():
    """Root endpoint returning API info."""
    return {"message": "Welcome to AddressBook API"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
