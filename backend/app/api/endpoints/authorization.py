"""
Authorization endpoints - Check permissions and get user capabilities.
"""
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.api.deps import get_current_active_user, require_permission, require_admin
from app.models.user import UserDB, UserResponse
from app.core.authorization import (
    rbac_manager, 
    Permission, 
    UserTier, 
    ActionRequest, 
    ActionRisk,
    AuthorizationDecision,
    AuditLogEntry
)

logger = logging.getLogger(__name__)
router = APIRouter()


class ActionAuthorizationRequest(BaseModel):
    """Request to check authorization for an action."""
    action_type: str
    action_description: str
    risk_level: str  # "safe", "low", "medium", "high", "critical"
    target_resource: Optional[str] = None
    requires_confirmation: bool = False


class ActionAuthorizationResponse(BaseModel):
    """Response with authorization decision."""
    authorized: bool
    requires_approval: bool
    reason: Optional[str]
    alternative_action: Optional[str]
    approval_required_from: Optional[List[str]]
    safety_warnings: List[str]


class UserCapabilities(BaseModel):
    """User's capabilities and permissions."""
    tier: str
    permissions: List[str]
    can_execute_risks: List[str]
    max_ticket_priority: int


class TicketAccessRequest(BaseModel):
    """Request to check ticket access."""
    ticket_id: str
    operation: str  # "view", "update", "delete"


@router.post("/authorize-action", response_model=ActionAuthorizationResponse)
async def authorize_action(
    request: ActionAuthorizationRequest,
    current_user: UserDB = Depends(get_current_active_user)
):
    """
    Check if user is authorized to perform a specific action.
    
    This endpoint is called before executing any automated troubleshooting action
    to ensure the user has the necessary permissions.
    """
    try:
        # Convert risk level string to enum
        try:
            risk_level = ActionRisk(request.risk_level.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid risk level: {request.risk_level}"
            )
        
        # Create action request
        action_request = ActionRequest(
            action_type=request.action_type,
            action_description=request.action_description,
            risk_level=risk_level,
            target_resource=request.target_resource,
            requires_confirmation=request.requires_confirmation
        )
        
        # Convert user to dict
        user_dict = {
            "id": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email,
            "tier": current_user.tier,
            "is_active": current_user.is_active
        }
        
        # Get authorization decision
        decision = rbac_manager.authorize_action(user_dict, action_request)
        
        return ActionAuthorizationResponse(
            authorized=decision.authorized,
            requires_approval=decision.requires_approval,
            reason=decision.reason,
            alternative_action=decision.alternative_action,
            approval_required_from=decision.approval_required_from or [],
            safety_warnings=decision.safety_warnings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authorization check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities", response_model=UserCapabilities)
async def get_user_capabilities(
    current_user: UserDB = Depends(get_current_active_user)
):
    """
    Get current user's capabilities and permissions.
    
    This is useful for the frontend to show/hide features based on user tier.
    """
    try:
        user_tier = UserTier(current_user.tier)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid user tier: {current_user.tier}"
        )
    
    # Get permissions
    permissions = rbac_manager.get_user_permissions(user_tier)
    
    # Determine which risk levels user can execute
    can_execute_risks = []
    if rbac_manager.check_permission(user_tier, Permission.EXECUTE_SAFE_ACTIONS):
        can_execute_risks.append("safe")
    if rbac_manager.check_permission(user_tier, Permission.EXECUTE_LOW_ACTIONS):
        can_execute_risks.append("low")
    if rbac_manager.check_permission(user_tier, Permission.EXECUTE_MEDIUM_ACTIONS):
        can_execute_risks.append("medium")
    if rbac_manager.check_permission(user_tier, Permission.EXECUTE_HIGH_ACTIONS):
        can_execute_risks.append("high")
    if rbac_manager.check_permission(user_tier, Permission.EXECUTE_CRITICAL_ACTIONS):
        can_execute_risks.append("critical")
    
    # Determine max ticket priority based on tier
    max_priority = {
        UserTier.CONTRACTOR: 3,
        UserTier.STAFF: 2,
        UserTier.MANAGER: 1,
        UserTier.ADMIN: 1
    }
    
    return UserCapabilities(
        tier=user_tier.value,
        permissions=permissions,
        can_execute_risks=can_execute_risks,
        max_ticket_priority=max_priority.get(user_tier, 3)
    )


@router.get("/audit-log", response_model=List[AuditLogEntry])
async def get_audit_log(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(require_permission(Permission.VIEW_AUDIT_LOG))
):
    """
    Get audit log entries.
    
    Requires VIEW_AUDIT_LOG permission (Manager or Admin only).
    """
    try:
        entries = rbac_manager.get_audit_log(
            user_id=user_id,
            limit=limit
        )
        return entries
    except Exception as e:
        logger.error(f"Error retrieving audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/permissions/check/{permission_name}")
async def check_permission(
    permission_name: str,
    current_user: UserDB = Depends(get_current_active_user)
):
    """
    Check if current user has a specific permission.
    
    Useful for frontend conditional rendering.
    """
    try:
        user_tier = UserTier(current_user.tier)
        permission = Permission(permission_name)
        
        has_permission = rbac_manager.check_permission(user_tier, permission)
        
        return {
            "user": current_user.email,
            "tier": user_tier.value,
            "permission": permission_name,
            "has_permission": has_permission
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/permissions/all")
async def get_all_permissions():
    """
    Get list of all available permissions in the system.
    
    Useful for admin UI and documentation.
    """
    return {
        "permissions": [p.value for p in Permission],
        "risk_levels": [r.value for r in ActionRisk],
        "user_tiers": [t.value for t in UserTier]
    }


class RolePermissionsResponse(BaseModel):
    """Permissions for a specific role."""
    tier: str
    permissions: List[str]


@router.get("/roles", response_model=List[RolePermissionsResponse])
async def get_all_roles(
    current_user: UserDB = Depends(require_admin)
):
    """
    Get all user tiers and their permissions.
    
    Admin only endpoint for viewing the complete permission matrix.
    """
    roles = []
    for tier in UserTier:
        permissions = rbac_manager.get_user_permissions(tier)
        roles.append(RolePermissionsResponse(
            tier=tier.value,
            permissions=permissions
        ))
    return roles
