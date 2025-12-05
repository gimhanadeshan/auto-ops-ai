"""
Admin endpoints for user management, role assignment, and audit logs.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import UserDB, UserResponse
from app.models.role import Role, Permission, ROLE_PERMISSIONS, ROLE_DESCRIPTIONS, RoleInfo
from app.models.audit_log import AuditLog, AuditLogFilter, AuditAction
from app.api.deps import require_permission, get_current_active_user
from app.services.audit_service import audit_service
from pydantic import BaseModel

router = APIRouter()


class UserRoleUpdate(BaseModel):
    """Schema for updating user role."""
    role: Role


class UserStatusUpdate(BaseModel):
    """Schema for updating user status."""
    is_active: bool


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[Role] = None,
    is_active: Optional[bool] = None,
    current_user: UserDB = Depends(require_permission(Permission.USER_VIEW)),
    db: Session = Depends(get_db)
):
    """
    List all users with optional filtering.
    Requires USER_VIEW permission (Support L1+ or Admin).
    """
    query = db.query(UserDB)
    
    if role:
        query = query.filter(UserDB.role == role.value)
    if is_active is not None:
        query = query.filter(UserDB.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    
    # Convert to response models with permissions
    return [UserResponse.from_db(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: UserDB = Depends(require_permission(Permission.USER_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID.
    Requires USER_VIEW permission.
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_db(user)


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: UserDB = Depends(require_permission(Permission.USER_MANAGE_ROLES)),
    db: Session = Depends(get_db)
):
    """
    Update a user's role.
    Requires USER_MANAGE_ROLES permission (IT Admin or System Admin only).
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_role = user.role
    user.role = role_update.role.value
    
    db.commit()
    db.refresh(user)
    
    # Log role change
    audit_service.log_action(
        db=db,
        action=AuditAction.USER_ROLE_CHANGE,
        success="success",
        user_email=current_user.email,
        user_role=current_user.role,
        resource_type="user",
        resource_id=str(user_id),
        details=f"Changed role from {old_role} to {role_update.role.value} for user {user.email}",
        action_metadata={"old_role": old_role, "new_role": role_update.role.value, "target_user": user.email}
    )
    
    return UserResponse.from_db(user)


@router.put("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    current_user: UserDB = Depends(require_permission(Permission.USER_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate a user.
    Requires USER_MANAGE permission (Support L3+ or Admin).
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-deactivation
    if user.id == current_user.id and not status_update.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    old_status = user.is_active
    user.is_active = status_update.is_active
    
    db.commit()
    db.refresh(user)
    
    # Log status change
    audit_service.log_action(
        db=db,
        action=AuditAction.USER_DEACTIVATE if not status_update.is_active else AuditAction.USER_UPDATE,
        success="success",
        user_email=current_user.email,
        user_role=current_user.role,
        resource_type="user",
        resource_id=str(user_id),
        details=f"Changed user {user.email} status from {old_status} to {status_update.is_active}",
        action_metadata={"old_status": old_status, "new_status": status_update.is_active, "target_user": user.email}
    )
    
    return UserResponse.from_db(user)


@router.get("/roles", response_model=List[RoleInfo])
async def list_roles(
    current_user: UserDB = Depends(require_permission(Permission.USER_VIEW))
):
    """
    List all available roles and their permissions.
    Requires USER_VIEW permission.
    """
    roles = []
    for role in Role:
        permissions = list(ROLE_PERMISSIONS.get(role, set()))
        roles.append(RoleInfo(
            role=role,
            permissions=[p.value for p in permissions],
            description=ROLE_DESCRIPTIONS.get(role, "")
        ))
    
    return roles


@router.get("/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_email: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    success: Optional[str] = None,
    current_user: UserDB = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with optional filtering.
    Requires SYSTEM_ADMIN permission (Admin only).
    """
    from app.models.audit_log import AuditLogDB
    from sqlalchemy import desc
    
    query = db.query(AuditLogDB)
    
    if user_email:
        query = query.filter(AuditLogDB.user_email == user_email)
    if action:
        query = query.filter(AuditLogDB.action == action)
    if resource_type:
        query = query.filter(AuditLogDB.resource_type == resource_type)
    if success:
        query = query.filter(AuditLogDB.success == success)
    
    logs = query.order_by(desc(AuditLogDB.timestamp)).offset(skip).limit(limit).all()
    
    return logs


@router.get("/audit-logs/me", response_model=List[AuditLog])
async def get_my_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for the current user.
    All authenticated users can view their own audit logs.
    """
    logs = audit_service.get_user_audit_logs(db, current_user.email, limit)
    return logs


@router.get("/audit-logs/failed-access")
async def get_failed_access_attempts(
    hours: int = Query(24, ge=1, le=168),
    current_user: UserDB = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get failed access attempts in the last N hours.
    Requires SYSTEM_ADMIN permission.
    Useful for security monitoring.
    """
    logs = audit_service.get_failed_access_attempts(db, hours)
    return logs
