"""Contact service for business logic."""

import uuid

from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


def create_contact(
    db: Session,
    contact: ContactCreate,
    user_id: uuid.UUID,
) -> Contact:
    """Create a new contact for a user."""
    db_contact = Contact(
        user_id=user_id,
        **contact.model_dump(),
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contact(
    db: Session,
    contact_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Contact | None:
    """Get a contact by ID, ensuring it belongs to the user."""
    return (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == user_id,
            Contact.is_active.is_(True),
        )
        .first()
    )


def get_contacts(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Contact], int]:
    """Get all active contacts for a user with pagination."""
    query = db.query(Contact).filter(
        Contact.user_id == user_id,
        Contact.is_active.is_(True),
    )

    total = query.count()
    contacts = query.offset(skip).limit(limit).all()

    return contacts, total


def update_contact(
    db: Session,
    contact_id: uuid.UUID,
    contact_update: ContactUpdate,
    user_id: uuid.UUID,
) -> Contact | None:
    """Update a contact."""
    db_contact = get_contact(db, contact_id, user_id)
    if not db_contact:
        return None

    # Update only provided fields
    update_data = contact_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact, field, value)

    db.commit()
    db.refresh(db_contact)
    return db_contact


def delete_contact(
    db: Session,
    contact_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """Soft delete a contact."""
    db_contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == user_id,
        )
        .first()
    )

    if not db_contact:
        return False

    db_contact.is_active = False
    db.commit()
    return True


def restore_contact(
    db: Session,
    contact_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """Restore a soft-deleted contact."""
    db_contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == user_id,
        )
        .first()
    )

    if not db_contact:
        return False

    db_contact.is_active = True
    db.commit()
    return True


def search_contacts(
    db: Session,
    user_id: uuid.UUID,
    search: str | None = None,
    tags: list[str] | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Contact], int]:
    """Search contacts by name, company, or filter by tags.

    Args:
        db: Database session
        user_id: User ID to filter contacts
        search: Search string for name/company (case-insensitive partial match)
        tags: List of tags to filter by (contacts must have ALL tags)
        skip: Pagination offset
        limit: Maximum results to return

    Returns:
        Tuple of (list of contacts, total count)
    """
    from sqlalchemy import or_

    query = db.query(Contact).filter(
        Contact.user_id == user_id,
        Contact.is_active.is_(True),
    )

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Contact.first_name.ilike(search_pattern),
                Contact.last_name.ilike(search_pattern),
                Contact.company.ilike(search_pattern),
            )
        )

    # Apply tag filter - fetch all and filter in Python for SQLite compatibility
    # In production with PostgreSQL, use Contact.tags.contains([tag]) for better performance
    if tags:
        contacts = query.all()
        filtered_contacts = [
            c for c in contacts
            if c.tags and all(tag in c.tags for tag in tags)
        ]
        total = len(filtered_contacts)
        return filtered_contacts[skip : skip + limit], total

    total = query.count()
    contacts = query.offset(skip).limit(limit).all()

    return contacts, total
