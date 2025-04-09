# external imports
from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

# Authenticated User Model
class AuthenticatedUser(BaseModel):
    success: bool
    user_id: Optional[str] = None
    organization_id: Optional[str] = None

class Organization(BaseModel):
    id: Optional[str] = None
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('id')
    def validate_uuid(cls, v):
        if v is not None:
            try:
                UUID(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v

# API Key Model
class APIKey(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    key: str
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: Optional[int] = 0

    @field_validator('id', 'user_id', 'organization_id')
    def validate_uuid(cls, v):
        if v is not None:
            try:
                UUID(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v

# User Organization Model
class UserOrganization(BaseModel):
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    role: Optional[str] = "member"
    created_at: Optional[datetime] = None

    @field_validator('user_id', 'organization_id')
    def validate_uuid(cls, v):
        if v is not None:
            try:
                UUID(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v

    class Config:
        from_attributes = True

class BearerToken(BaseModel):
    access_token: str
    refresh_token: str

class OrganizationWithRole(BaseModel):
    id: str
    name: str
    role: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('id')
    def validate_uuid(cls, v):
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")

class Profile(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    default_organization: Optional[str] = None
    created_at: Optional[datetime] = None
    
    @field_validator('id')
    def validate_uuid(cls, v):
        if v is not None:
            try:
                UUID(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v