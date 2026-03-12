"""Pydantic schemas for contact requests and responses."""

import uuid
from datetime import date, datetime
from typing import Any, List, Optional

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
    
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class ContactBase(BaseModel):
    """Base contact schema with common fields."""
    
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=200)
    department: Optional[str] = Field(None, max_length=200)
    emails: List[EmailSchema] = []
    phones: List[PhoneSchema] = []
    address: Optional[AddressSchema] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    tags: List[str] = []
    
    model_config = {"from_attributes": True}


class ContactCreate(ContactBase):
    """Schema for creating a new contact."""
    
    pass


class ContactUpdate(BaseModel):
    """Schema for updating an existing contact (all fields optional)."""
    
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=200)
    department: Optional[str] = Field(None, max_length=200)
    emails: Optional[List[EmailSchema]] = None
    phones: Optional[List[PhoneSchema]] = None
    address: Optional[AddressSchema] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    
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
    
    items: List[ContactResponse]
    total: int
    page: int
    page_size: int
    pages: int
    
    model_config = {"from_attributes": True}
