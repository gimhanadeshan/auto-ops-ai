"""
User management endpoints (Admin only)
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserDB, UserResponse, UserRegister
from app.core.security import get_password_hash
from app.api.deps import get_current_user
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class UserUpdate(BaseModel):
    """User update model (admin can update any user)"""
    name: str = None
    tier: str = None
    is_active: bool = None


class UserStatusToggle(BaseModel):
    """Toggle user active status"""
    is_active: bool


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only)
    """
    # Check if user is admin
    if current_user.tier != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can list users"
        )
    
    try:
        users = db.query(UserDB).all()
        return users
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserRegister,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user (Admin only)
    """
    # Check if user is admin
    if current_user.tier != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users"
        )
    
    try:
        # Check if user already exists
        existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        new_user = UserDB(
            email=user_data.email,
            name=user_data.name,
            hashed_password=get_password_hash(user_data.password),
            tier=user_data.tier,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Admin {current_user.email} created user: {new_user.email}")
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a user (Admin only)
    """
    # Check if user is admin
    if current_user.tier != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update users"
        )
    
    try:
        # Get user to update
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        if user_update.name is not None:
            user.name = user_update.name
        if user_update.tier is not None:
            user.tier = user_update.tier
        if user_update.is_active is not None:
            user.is_active = user_update.is_active
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"Admin {current_user.email} updated user: {user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.patch("/users/{user_id}/status", response_model=UserResponse)
async def toggle_user_status(
    user_id: int,
    status_update: UserStatusToggle,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle user active status (Admin only)
    """
    # Check if user is admin
    if current_user.tier != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change user status"
        )
    
    try:
        # Get user
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from deactivating themselves
        if user.id == current_user.id and not status_update.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account"
            )
        
        user.is_active = status_update.is_active
        db.commit()
        db.refresh(user)
        
        action = "activated" if status_update.is_active else "deactivated"
        logger.info(f"Admin {current_user.email} {action} user: {user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle user status: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user status"
        )


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user (Admin only)
    """
    # Check if user is admin
    if current_user.tier != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete users"
        )
    
    try:
        # Get user
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own account"
            )
        
        db.delete(user)
        db.commit()
        
        logger.info(f"Admin {current_user.email} deleted user: {user.email}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
