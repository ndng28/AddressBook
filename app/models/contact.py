"""Contact model for storing contact information."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Contact(Base):
    """Contact model for storing personal and professional contact information."""

    __tablename__ = "contacts"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Name fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    # Professional info
    company = Column(String(200), nullable=True)
    job_title = Column(String(200), nullable=True)
    department = Column(String(200), nullable=True)

    # Contact methods (stored as JSON for flexibility)
    emails = Column(JSON, default=list)
    phones = Column(JSON, default=list)

    # Address (stored as JSON)
    address = Column(JSON, nullable=True)

    # Personal info
    birthday = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    tags = Column(JSON, default=list)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    user = relationship("User", back_populates="contacts")

    @property
    def full_name(self) -> str:
        """Return full name combining first and last name."""
        parts = [p for p in [self.first_name, self.last_name] if p]
        return " ".join(parts) if parts else "Unknown"
