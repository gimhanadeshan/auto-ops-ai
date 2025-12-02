"""
User models for database and API.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr
from app.core.database import Base


# SQLAlchemy Model
class UserDB(Base):
    """User database model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)  # User's full name
    hashed_password = Column(String, nullable=False)
    tier = Column(String, default="staff")  # staff, manager, contractor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Pydantic Models for API
class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    name: str
    password: str
    tier: str = "staff"  # staff, manager, contractor


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response (without password)."""
    id: int
    email: str
    name: str
    tier: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
