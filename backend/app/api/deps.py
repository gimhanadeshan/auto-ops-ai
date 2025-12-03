"""
API dependencies - Database sessions, authentication, authorization, etc.
"""
from typing import Optional, Generator, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.core.authorization import rbac_manager, Permission, UserTier, ActionRequest, ActionRisk
from app.models.user import UserDB

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[UserDB]:
    """
    Get current authenticated user from JWT token.
    Validates token and retrieves user from database.
    """
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get email from token payload
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database by email
        user = db.query(UserDB).filter(UserDB.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(
    current_user: UserDB = Depends(get_current_user)
) -> UserDB:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user


def get_current_user_email(
    current_user: UserDB = Depends(get_current_active_user)
) -> str:
    """Get email of current authenticated user."""
    return current_user.email


# ============================================================================
# Authorization Dependencies (RBAC)
# ============================================================================

def require_permission(permission: Permission) -> Callable:
    """
    Dependency factory that requires a specific permission.
    Usage: current_user: UserDB = Depends(require_permission(Permission.VIEW_ALL_TICKETS))
    """
    def permission_checker(current_user: UserDB = Depends(get_current_active_user)) -> UserDB:
        try:
            user_tier = UserTier(current_user.tier)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid user tier: {current_user.tier}"
            )
        
        if not rbac_manager.check_permission(user_tier, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required"
            )
        
        return current_user
    
    return permission_checker


def require_tier(min_tier: UserTier) -> Callable:
    """
    Dependency factory that requires a minimum user tier.
    Usage: current_user: UserDB = Depends(require_tier(UserTier.MANAGER))
    """
    tier_hierarchy = {
        UserTier.CONTRACTOR: 0,
        UserTier.STAFF: 1,
        UserTier.MANAGER: 2,
        UserTier.ADMIN: 3
    }
    
    def tier_checker(current_user: UserDB = Depends(get_current_active_user)) -> UserDB:
        try:
            user_tier = UserTier(current_user.tier)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid user tier: {current_user.tier}"
            )
        
        if tier_hierarchy[user_tier] < tier_hierarchy[min_tier]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {min_tier.value} tier or higher required"
            )
        
        return current_user
    
    return tier_checker


# Convenience dependencies for common tier requirements
def require_staff(current_user: UserDB = Depends(require_tier(UserTier.STAFF))) -> UserDB:
    """Require at least staff tier."""
    return current_user


def require_manager(current_user: UserDB = Depends(require_tier(UserTier.MANAGER))) -> UserDB:
    """Require at least manager tier."""
    return current_user


def require_admin(current_user: UserDB = Depends(require_tier(UserTier.ADMIN))) -> UserDB:
    """Require admin tier."""
    return current_user


def authorize_action(
    action_request: ActionRequest,
    current_user: UserDB = Depends(get_current_active_user)
):
    """
    Authorize an action based on user tier and action risk level.
    Returns authorization decision or raises HTTPException.
    """
    user_dict = {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "tier": current_user.tier,
        "is_active": current_user.is_active
    }
    
    decision = rbac_manager.authorize_action(user_dict, action_request)
    
    if not decision.authorized:
        if decision.requires_approval:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": decision.reason,
                    "requires_approval": True,
                    "approval_required_from": decision.approval_required_from,
                    "alternative_action": decision.alternative_action
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": decision.reason,
                    "alternative_action": decision.alternative_action
                }
            )
    
    return decision
