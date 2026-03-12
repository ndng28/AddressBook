"""Pydantic schemas for contact requests and responses."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, model_validator


class EmailSchema(BaseModel):
    """Schema for email address with type."""

    email: EmailStr
    type: str = Field(default="work", pattern="^(work|personal|other)$")
    is_primary: bool = False


class PhoneSchema(BaseModel):
    """Schema for phone number with type."""

    number: str = Field(..., min_length=5, max_length=20)
    type: str = Field(default="mobile", pattern="^(mobile|work|home|other)$")
    is_primary: bool = False


class AddressSchema(BaseModel):
    """Schema for address."""

    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


class ContactBase(BaseModel):
    """Base contact schema with common fields."""

    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    company: str | None = Field(None, max_length=200)
    job_title: str | None = Field(None, max_length=200)
    department: str | None = Field(None, max_length=200)
    emails: list[EmailSchema] = []
    phones: list[PhoneSchema] = []
    address: AddressSchema | None = None
    birthday: date | None = None
    notes: str | None = None
    photo_url: str | None = Field(None, max_length=500)
    tags: list[str] = []

    model_config = {"from_attributes": True}


class ContactCreate(ContactBase):
    """Schema for creating a new contact."""

    pass


class ContactUpdate(BaseModel):
    """Schema for updating an existing contact (all fields optional)."""

    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    company: str | None = Field(None, max_length=200)
    job_title: str | None = Field(None, max_length=200)
    department: str | None = Field(None, max_length=200)
    emails: list[EmailSchema] | None = None
    phones: list[PhoneSchema] | None = None
    address: AddressSchema | None = None
    birthday: date | None = None
    notes: str | None = None
    photo_url: str | None = Field(None, max_length=500)
    tags: list[str] | None = None

    model_config = {"from_attributes": True}


class ContactResponse(ContactBase):
    """Schema for contact response."""

    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str = ""
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def compute_full_name(self) -> "ContactResponse":
        """Compute full name from first and last name."""
        # Only compute if full_name is empty
        if not self.full_name:
            first = self.first_name or ""
            last = self.last_name or ""
            parts = [p.strip() for p in [first, last] if p and p.strip()]
            self.full_name = " ".join(parts) if parts else "Unknown"
        return self

    model_config = {"from_attributes": True}


class ContactListResponse(BaseModel):
    """Schema for paginated contact list response."""

    items: list[ContactResponse]
    total: int
    page: int
    page_size: int
    pages: int

    model_config = {"from_attributes": True}
