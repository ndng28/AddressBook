"""FastAPI application for AddressBook."""

from fastapi import FastAPI

app = FastAPI(
    title="AddressBook API",
    description="A FastAPI application for managing contacts",
    version="0.1.0",
)


@app.get("/")
def root():
    """Root endpoint returning API info."""
    return {"message": "Welcome to AddressBook API"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
