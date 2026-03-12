"""Pydantic schemas for user requests and responses."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr
    full_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr
    password: str
    
    model_config = {"from_attributes": True}


class UserResponse(UserBase):
    """Schema for user response (excludes password)."""
    
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str
    token_type: str = "bearer"
    
    model_config = {"from_attributes": True}
