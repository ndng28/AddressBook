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
