"""
Role-Based Access Control (RBAC) System
Implements fine-grained authorization for IT Support operations.
"""
from enum import Enum
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class UserTier(Enum):
    """User tier hierarchy for access control."""
    CONTRACTOR = "contractor"  # Limited access, external users
    STAFF = "staff"            # Regular employees
    MANAGER = "manager"        # Department managers
    ADMIN = "admin"            # IT administrators


class ActionRisk(Enum):
    """Risk level classification for actions."""
    SAFE = "safe"              # Read-only, diagnostic (network test, disk check)
    LOW = "low"                # Non-destructive (clear cache, restart app)
    MEDIUM = "medium"          # System changes (restart service, modify settings)
    HIGH = "high"              # Critical operations (system restart, driver update)
    CRITICAL = "critical"      # Destructive (delete data, format, system-wide changes)


class Permission(Enum):
    """System permissions."""
    # Ticket operations
    CREATE_TICKET = "create_ticket"
    VIEW_OWN_TICKETS = "view_own_tickets"
    VIEW_ALL_TICKETS = "view_all_tickets"
    UPDATE_OWN_TICKETS = "update_own_tickets"
    UPDATE_ALL_TICKETS = "update_all_tickets"
    DELETE_TICKET = "delete_ticket"
    ESCALATE_TICKET = "escalate_ticket"
    
    # Troubleshooting actions
    RUN_DIAGNOSTICS = "run_diagnostics"
    EXECUTE_SAFE_ACTIONS = "execute_safe_actions"
    EXECUTE_LOW_ACTIONS = "execute_low_actions"
    EXECUTE_MEDIUM_ACTIONS = "execute_medium_actions"
    EXECUTE_HIGH_ACTIONS = "execute_high_actions"
    EXECUTE_CRITICAL_ACTIONS = "execute_critical_actions"
    
    # System operations
    VIEW_MONITORING = "view_monitoring"
    VIEW_REPORTS = "view_reports"
    VIEW_KNOWLEDGE_BASE = "view_knowledge_base"
    EDIT_KNOWLEDGE_BASE = "edit_knowledge_base"
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOG = "view_audit_log"
    SYSTEM_SETTINGS = "system_settings"


class ActionRequest(BaseModel):
    """Request to perform an action."""
    action_type: str
    action_description: str
    risk_level: ActionRisk
    target_resource: Optional[str] = None
    requires_confirmation: bool = False
    metadata: Dict = {}


class AuthorizationDecision(BaseModel):
    """Result of authorization check."""
    authorized: bool
    requires_approval: bool = False
    reason: Optional[str] = None
    alternative_action: Optional[str] = None
    approval_required_from: Optional[List[str]] = None
    safety_warnings: List[str] = []


class AuditLogEntry(BaseModel):
    """Audit log entry for tracking all authorization decisions."""
    timestamp: datetime
    user_id: str
    user_name: str
    user_tier: str
    action_type: str
    risk_level: str
    decision: str
    reason: str
    resource: Optional[str] = None
    metadata: Dict = {}


class RBACManager:
    """
    Role-Based Access Control Manager
    Enforces authorization policies based on user tier and action risk.
    """
    
    def __init__(self):
        self.audit_log: List[AuditLogEntry] = []
        self._initialize_role_permissions()
    
    def _initialize_role_permissions(self):
        """Define permission matrix for each user tier."""
        self.role_permissions: Dict[UserTier, Set[Permission]] = {
            UserTier.CONTRACTOR: {
                Permission.CREATE_TICKET,
                Permission.VIEW_OWN_TICKETS,
                Permission.UPDATE_OWN_TICKETS,
                Permission.VIEW_KNOWLEDGE_BASE,
                Permission.RUN_DIAGNOSTICS,
                # Contractors can only execute SAFE actions
                Permission.EXECUTE_SAFE_ACTIONS,
            },
            UserTier.STAFF: {
                Permission.CREATE_TICKET,
                Permission.VIEW_OWN_TICKETS,
                Permission.VIEW_ALL_TICKETS,
                Permission.UPDATE_OWN_TICKETS,
                Permission.ESCALATE_TICKET,
                Permission.VIEW_KNOWLEDGE_BASE,
                Permission.VIEW_MONITORING,
                Permission.VIEW_REPORTS,
                Permission.RUN_DIAGNOSTICS,
                Permission.EXECUTE_SAFE_ACTIONS,
                Permission.EXECUTE_LOW_ACTIONS,
            },
            UserTier.MANAGER: {
                Permission.CREATE_TICKET,
                Permission.VIEW_OWN_TICKETS,
                Permission.VIEW_ALL_TICKETS,
                Permission.UPDATE_OWN_TICKETS,
                Permission.UPDATE_ALL_TICKETS,
                Permission.ESCALATE_TICKET,
                Permission.VIEW_KNOWLEDGE_BASE,
                Permission.EDIT_KNOWLEDGE_BASE,
                Permission.VIEW_MONITORING,
                Permission.VIEW_REPORTS,
                Permission.VIEW_AUDIT_LOG,
                Permission.RUN_DIAGNOSTICS,
                Permission.EXECUTE_SAFE_ACTIONS,
                Permission.EXECUTE_LOW_ACTIONS,
                Permission.EXECUTE_MEDIUM_ACTIONS,
            },
            UserTier.ADMIN: {
                # Admins have all permissions
                Permission.CREATE_TICKET,
                Permission.VIEW_OWN_TICKETS,
                Permission.VIEW_ALL_TICKETS,
                Permission.UPDATE_OWN_TICKETS,
                Permission.UPDATE_ALL_TICKETS,
                Permission.DELETE_TICKET,
                Permission.ESCALATE_TICKET,
                Permission.VIEW_KNOWLEDGE_BASE,
                Permission.EDIT_KNOWLEDGE_BASE,
                Permission.VIEW_MONITORING,
                Permission.VIEW_REPORTS,
                Permission.VIEW_AUDIT_LOG,
                Permission.MANAGE_USERS,
                Permission.SYSTEM_SETTINGS,
                Permission.RUN_DIAGNOSTICS,
                Permission.EXECUTE_SAFE_ACTIONS,
                Permission.EXECUTE_LOW_ACTIONS,
                Permission.EXECUTE_MEDIUM_ACTIONS,
                Permission.EXECUTE_HIGH_ACTIONS,
                Permission.EXECUTE_CRITICAL_ACTIONS,
            }
        }
        
        # Define risk-based action rules
        self.risk_action_mapping = {
            ActionRisk.SAFE: Permission.EXECUTE_SAFE_ACTIONS,
            ActionRisk.LOW: Permission.EXECUTE_LOW_ACTIONS,
            ActionRisk.MEDIUM: Permission.EXECUTE_MEDIUM_ACTIONS,
            ActionRisk.HIGH: Permission.EXECUTE_HIGH_ACTIONS,
            ActionRisk.CRITICAL: Permission.EXECUTE_CRITICAL_ACTIONS,
        }
    
    def check_permission(self, user_tier: UserTier, permission: Permission) -> bool:
        """Check if a user tier has a specific permission."""
        return permission in self.role_permissions.get(user_tier, set())
    
    def authorize_action(
        self, 
        user: Dict, 
        action: ActionRequest
    ) -> AuthorizationDecision:
        """
        Authorize an action based on user tier, action risk, and current context.
        
        Args:
            user: User object with id, name, email, tier, is_active
            action: ActionRequest with risk level and description
            
        Returns:
            AuthorizationDecision with authorization status and details
        """
        decision = AuthorizationDecision(
            authorized=False,
            requires_approval=False,
            reason=None,
            safety_warnings=[]
        )
        
        # Check 1: User must be active
        if not user.get("is_active", False):
            decision.reason = "User account is inactive or suspended"
            self._log_audit(user, action, "DENIED", decision.reason)
            return decision
        
        # Get user tier
        try:
            user_tier = UserTier(user.get("tier", "staff"))
        except ValueError:
            decision.reason = f"Invalid user tier: {user.get('tier')}"
            self._log_audit(user, action, "DENIED", decision.reason)
            return decision
        
        # Check 2: Check if user has permission for this risk level
        required_permission = self.risk_action_mapping.get(action.risk_level)
        if not required_permission:
            decision.reason = f"Unknown risk level: {action.risk_level}"
            self._log_audit(user, action, "DENIED", decision.reason)
            return decision
        
        has_permission = self.check_permission(user_tier, required_permission)
        
        if not has_permission:
            decision.reason = (
                f"{user_tier.value} tier is not authorized to execute "
                f"{action.risk_level.value} risk actions"
            )
            decision.alternative_action = "Please request assistance from a manager or admin"
            decision.approval_required_from = ["manager", "admin"]
            self._log_audit(user, action, "DENIED", decision.reason)
            return decision
        
        # Check 3: Apply special rules based on tier
        if user_tier == UserTier.CONTRACTOR:
            # Contractors always need approval, even for SAFE actions
            decision.authorized = False
            decision.requires_approval = True
            decision.reason = "Contractor tier requires approval for all automated actions"
            decision.approval_required_from = ["staff", "manager", "admin"]
            self._log_audit(user, action, "REQUIRES_APPROVAL", decision.reason)
            return decision
        
        # Check 4: Apply approval rules based on risk level
        if action.risk_level in [ActionRisk.MEDIUM, ActionRisk.HIGH, ActionRisk.CRITICAL]:
            if user_tier == UserTier.STAFF:
                decision.authorized = False
                decision.requires_approval = True
                decision.reason = f"{action.risk_level.value} risk actions require manager approval"
                decision.approval_required_from = ["manager", "admin"]
                self._log_audit(user, action, "REQUIRES_APPROVAL", decision.reason)
                return decision
            elif user_tier == UserTier.MANAGER and action.risk_level == ActionRisk.CRITICAL:
                decision.authorized = False
                decision.requires_approval = True
                decision.reason = "Critical actions require admin approval"
                decision.approval_required_from = ["admin"]
                self._log_audit(user, action, "REQUIRES_APPROVAL", decision.reason)
                return decision
        
        # Check 5: Add safety warnings
        decision.safety_warnings = self._generate_safety_warnings(action)
        
        # Authorization granted
        decision.authorized = True
        decision.requires_approval = action.requires_confirmation
        decision.reason = "Authorization granted based on user tier and permissions"
        self._log_audit(user, action, "APPROVED", decision.reason)
        
        return decision
    
    def _generate_safety_warnings(self, action: ActionRequest) -> List[str]:
        """Generate safety warnings based on action risk level."""
        warnings = []
        
        if action.risk_level == ActionRisk.LOW:
            warnings.append("This action will clear temporary data and may require application restart.")
        elif action.risk_level == ActionRisk.MEDIUM:
            warnings.append("This action will modify system settings. Please ensure no critical work is in progress.")
        elif action.risk_level == ActionRisk.HIGH:
            warnings.append("⚠️ This is a high-risk action that may cause system downtime. Save all work before proceeding.")
        elif action.risk_level == ActionRisk.CRITICAL:
            warnings.append("🚨 CRITICAL ACTION: This may result in data loss or system instability. Ensure you have backups.")
        
        if action.requires_confirmation:
            warnings.append("User confirmation required before execution.")
        
        return warnings
    
    def authorize_ticket_access(
        self,
        user: Dict,
        ticket: Dict,
        operation: str  # "view", "update", "delete"
    ) -> AuthorizationDecision:
        """
        Authorize access to a specific ticket.
        
        Args:
            user: User object
            ticket: Ticket object with user_id
            operation: Type of operation (view, update, delete)
        """
        decision = AuthorizationDecision(authorized=False)
        user_tier = UserTier(user.get("tier", "staff"))
        
        # Check if user owns the ticket
        is_owner = ticket.get("user_id") == user.get("id")
        
        if operation == "view":
            # Contractors and staff can only view their own tickets
            if user_tier in [UserTier.CONTRACTOR, UserTier.STAFF]:
                if is_owner:
                    decision.authorized = True
                    decision.reason = "User can view their own tickets"
                else:
                    decision.reason = f"{user_tier.value} tier can only view their own tickets"
            else:
                # Managers and admins can view all tickets
                decision.authorized = True
                decision.reason = "User has permission to view all tickets"
        
        elif operation == "update":
            # Contractors and staff can update their own tickets
            if user_tier in [UserTier.CONTRACTOR, UserTier.STAFF]:
                if is_owner:
                    decision.authorized = True
                    decision.reason = "User can update their own tickets"
                else:
                    decision.reason = f"{user_tier.value} tier can only update their own tickets"
            else:
                # Managers and admins can update all tickets
                decision.authorized = True
                decision.reason = "User has permission to update all tickets"
        
        elif operation == "delete":
            # Only admins can delete tickets
            if user_tier == UserTier.ADMIN:
                decision.authorized = True
                decision.reason = "Admin can delete tickets"
            else:
                decision.reason = "Only administrators can delete tickets"
                decision.alternative_action = "You can close or archive the ticket instead"
        
        return decision
    
    def _log_audit(
        self,
        user: Dict,
        action: ActionRequest,
        decision: str,
        reason: str
    ):
        """Log authorization decision to audit trail."""
        entry = AuditLogEntry(
            timestamp=datetime.utcnow(),
            user_id=user.get("id", "unknown"),
            user_name=user.get("name", "Unknown User"),
            user_tier=user.get("tier", "unknown"),
            action_type=action.action_type,
            risk_level=action.risk_level.value,
            decision=decision,
            reason=reason,
            resource=action.target_resource,
            metadata=action.metadata
        )
        self.audit_log.append(entry)
        
        # Also log to application logger
        logger.info(
            f"Authorization: {decision} | User: {entry.user_name} ({entry.user_tier}) | "
            f"Action: {entry.action_type} ({entry.risk_level}) | Reason: {reason}"
        )
    
    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """
        Retrieve audit log entries with optional filters.
        
        Args:
            user_id: Filter by specific user
            start_time: Filter entries after this time
            end_time: Filter entries before this time
            limit: Maximum number of entries to return
        """
        filtered_log = self.audit_log
        
        if user_id:
            filtered_log = [e for e in filtered_log if e.user_id == user_id]
        
        if start_time:
            filtered_log = [e for e in filtered_log if e.timestamp >= start_time]
        
        if end_time:
            filtered_log = [e for e in filtered_log if e.timestamp <= end_time]
        
        # Sort by timestamp descending (newest first)
        filtered_log = sorted(filtered_log, key=lambda x: x.timestamp, reverse=True)
        
        return filtered_log[:limit]
    
    def get_user_permissions(self, user_tier: UserTier) -> List[str]:
        """Get list of all permissions for a user tier."""
        permissions = self.role_permissions.get(user_tier, set())
        return [p.value for p in permissions]


# Global RBAC manager instance
rbac_manager = RBACManager()
