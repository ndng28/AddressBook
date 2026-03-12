"""Contact router for managing contacts."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import (
    ContactCreate,
    ContactListResponse,
    ContactResponse,
    ContactUpdate,
)
from app.services.contact_service import (
    create_contact,
    delete_contact,
    get_contact,
    get_contacts,
    restore_contact,
    update_contact,
)
from app.services.user_service import get_user_by_email
from app.utils.auth import decode_token

router = APIRouter(prefix="/api/v1/contacts", tags=["contacts"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    email_obj = payload.get("sub")
    if email_obj is None or not isinstance(email_obj, str):
        raise credentials_exception

    email: str = email_obj

    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user


def get_deleted_contacts(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Contact], int]:
    """Get all soft-deleted contacts for a user with pagination."""

    query = db.query(Contact).filter(
        Contact.user_id == user_id,
        Contact.is_active.is_(False),
    )

    total = query.count()
    contacts = query.offset(skip).limit(limit).all()

    return contacts, total


# ============================================================
# Static routes (must be defined BEFORE parameterized routes)
# ============================================================


@router.get("", response_model=ContactListResponse)
def list_contacts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of records to return"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all active contacts for the current user with pagination.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return (1-100)
        current_user: The authenticated user
        db: Database session

    Returns:
        Paginated list of contacts
    """
    contacts, total = get_contacts(db, current_user.id, skip=skip, limit=limit)

    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1

    return ContactListResponse(
        items=contacts,
        total=total,
        page=page,
        page_size=limit,
        pages=pages,
    )


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_new_contact(
    contact: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new contact for the current user.

    Args:
        contact: Contact creation data
        current_user: The authenticated user
        db: Database session

    Returns:
        The created contact with generated ID

    Raises:
        HTTPException: If contact data is invalid
    """
    return create_contact(db, contact, current_user.id)


@router.get("/deleted", response_model=ContactListResponse)
def list_deleted_contacts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of records to return"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all soft-deleted contacts for the current user.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return (1-100)
        current_user: The authenticated user
        db: Database session

    Returns:
        Paginated list of deleted contacts
    """
    contacts, total = get_deleted_contacts(db, current_user.id, skip=skip, limit=limit)

    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1

    return ContactListResponse(
        items=contacts,
        total=total,
        page=page,
        page_size=limit,
        pages=pages,
    )


# ============================================================
# Parameterized routes with UUID (defined AFTER static routes)
# ============================================================


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact_details(
    contact_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific contact.

    Args:
        contact_id: UUID of the contact to retrieve
        current_user: The authenticated user
        db: Database session

    Returns:
        Contact details

    Raises:
        HTTPException: 404 if contact not found, 403 if contact belongs to another user
    """
    contact = get_contact(db, contact_id, current_user.id)

    if not contact:
        # Check if contact exists but belongs to another user
        other_contact = (
            db.query(Contact)
            .filter(
                Contact.id == contact_id,
                Contact.user_id != current_user.id,
            )
            .first()
        )

        if other_contact:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this contact",
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
def update_contact_details(
    contact_id: uuid.UUID,
    contact_update: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing contact.

    Args:
        contact_id: UUID of the contact to update
        contact_update: Contact update data (only provided fields are updated)
        current_user: The authenticated user
        db: Database session

    Returns:
        Updated contact

    Raises:
        HTTPException: 404 if contact not found, 403 if contact belongs to another user
    """
    # First check if contact exists and belongs to user
    contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id,
            Contact.is_active.is_(True),
        )
        .first()
    )

    if not contact:
        # Check if contact exists but belongs to another user
        other_contact = (
            db.query(Contact)
            .filter(
                Contact.id == contact_id,
                Contact.user_id != current_user.id,
            )
            .first()
        )

        if other_contact:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this contact",
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    updated = update_contact(db, contact_id, contact_update, current_user.id)
    return updated


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact_endpoint(
    contact_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft delete a contact.

    Args:
        contact_id: UUID of the contact to delete
        current_user: The authenticated user
        db: Database session

    Raises:
        HTTPException: 404 if contact not found, 403 if contact belongs to another user
    """
    # Check if contact exists and belongs to user
    contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id,
        )
        .first()
    )

    if not contact:
        # Check if contact exists but belongs to another user
        other_contact = (
            db.query(Contact)
            .filter(
                Contact.id == contact_id,
                Contact.user_id != current_user.id,
            )
            .first()
        )

        if other_contact:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this contact",
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    delete_contact(db, contact_id, current_user.id)
    return None


@router.post("/{contact_id}/restore", response_model=ContactResponse)
def restore_deleted_contact(
    contact_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Restore a soft-deleted contact.

    Args:
        contact_id: UUID of the contact to restore
        current_user: The authenticated user
        db: Database session

    Returns:
        Restored contact

    Raises:
        HTTPException: 404 if contact not found, 403 if contact belongs to another user
    """
    # Check if contact exists and belongs to user
    contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id,
        )
        .first()
    )

    if not contact:
        # Check if contact exists but belongs to another user
        other_contact = (
            db.query(Contact)
            .filter(
                Contact.id == contact_id,
                Contact.user_id != current_user.id,
            )
            .first()
        )

        if other_contact:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to restore this contact",
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    success = restore_contact(db, contact_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restore contact",
        )

    # Return the restored contact
    db.refresh(contact)
    return contact
