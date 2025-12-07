# RBAC System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           AUTO-OPS AI RBAC SYSTEM                             │
│                    Role-Based Access Control Implementation                   │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                              USER HIERARCHY                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│                         System Admin (Full Access)                            │
│                                    │                                          │
│                    ┌───────────────┴───────────────┐                         │
│                    │                                │                         │
│              IT Admin                          Support L3                     │
│           (IT Operations)                  (Senior Engineer)                  │
│                                                     │                         │
│                                         ┌───────────┴───────────┐            │
│                                         │                       │            │
│                                   Support L2              Support L1         │
│                               (Advanced Support)      (Basic Support)        │
│                                                                               │
│              Manager                                                          │
│           (Team Lead)                                                         │
│                │                                                              │
│        ┌───────┴───────┐                                                     │
│        │               │                                                     │
│      Staff       Contractor                                                  │
│   (Employee)    (External)                                                   │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         PERMISSION CATEGORIES                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  📋 TICKET PERMISSIONS                                                        │
│     • ticket:view:own         - View own tickets                             │
│     • ticket:view:team        - View team tickets                            │
│     • ticket:view:all         - View all tickets                             │
│     • ticket:create           - Create new tickets                           │
│     • ticket:update:own       - Update own tickets                           │
│     • ticket:update:any       - Update any ticket                            │
│     • ticket:delete:any       - Delete tickets                               │
│     • ticket:assign           - Assign tickets                               │
│     • ticket:escalate         - Escalate tickets                             │
│                                                                               │
│  🔧 TROUBLESHOOTING PERMISSIONS                                               │
│     • troubleshoot:run        - Run diagnostics                              │
│     • troubleshoot:auto_resolve - Auto-resolve issues                        │
│     • troubleshoot:view_logs  - View troubleshooting logs                    │
│                                                                               │
│  🖥️  SYSTEM PERMISSIONS                                                       │
│     • system:monitor          - System monitoring                            │
│     • system:diagnostics      - Run system diagnostics                       │
│     • system:admin            - System administration                        │
│                                                                               │
│  👥 USER MANAGEMENT PERMISSIONS                                               │
│     • user:view               - View users                                   │
│     • user:manage             - Manage users                                 │
│     • user:manage_roles       - Change user roles                            │
│                                                                               │
│  📊 DASHBOARD & REPORTS                                                       │
│     • dashboard:view          - View dashboard                               │
│     • reports:view            - View reports                                 │
│     • reports:export          - Export reports                               │
│                                                                               │
│  📚 KNOWLEDGE BASE                                                            │
│     • kb:view                 - View knowledge base                          │
│     • kb:edit                 - Edit knowledge base                          │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         REQUEST FLOW WITH RBAC                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  1. USER REQUEST                                                              │
│     │                                                                         │
│     │  POST /api/tickets/123/troubleshoot                                    │
│     │  Authorization: Bearer eyJ...                                          │
│     │                                                                         │
│     ▼                                                                         │
│  2. AUTHENTICATION (deps.py)                                                  │
│     │                                                                         │
│     │  • Verify JWT token                                                    │
│     │  • Extract user email                                                  │
│     │  • Load user from database                                             │
│     │  • Check if user is active                                             │
│     │                                                                         │
│     ▼                                                                         │
│  3. AUTHORIZATION (deps.py)                                                   │
│     │                                                                         │
│     │  • Get user's role (e.g., support_l1)                                  │
│     │  • Get role's permissions                                              │
│     │  • Check if has required permission (troubleshoot:run)                 │
│     │                                                                         │
│     ├──► ❌ PERMISSION DENIED                                                │
│     │     • Log access denied to audit_logs                                  │
│     │     • Return 403 Forbidden                                             │
│     │     • Show error message to user                                       │
│     │                                                                         │
│     └──► ✅ PERMISSION GRANTED                                               │
│           │                                                                   │
│           ▼                                                                   │
│  4. RESOURCE ACCESS CHECK (tickets.py)                                        │
│     │                                                                         │
│     │  • Get ticket from database                                            │
│     │  • Check if user can view/modify this ticket                           │
│     │  • Verify ticket ownership if needed                                   │
│     │                                                                         │
│     ├──► ❌ ACCESS DENIED                                                    │
│     │     • Log to audit_logs                                                │
│     │     • Return 403 Forbidden                                             │
│     │                                                                         │
│     └──► ✅ ACCESS GRANTED                                                   │
│           │                                                                   │
│           ▼                                                                   │
│  5. EXECUTE ACTION (ticket_service.py)                                        │
│     │                                                                         │
│     │  • Run troubleshooting                                                 │
│     │  • Update ticket                                                       │
│     │  • Generate diagnostics                                                │
│     │                                                                         │
│     ▼                                                                         │
│  6. AUDIT LOGGING (audit_service.py)                                          │
│     │                                                                         │
│     │  • Log action to audit_logs table                                      │
│     │  • Record: user, action, resource, timestamp, result                   │
│     │  • Also log to application logs                                        │
│     │                                                                         │
│     ▼                                                                         │
│  7. RETURN RESPONSE                                                           │
│     │                                                                         │
│     │  200 OK                                                                │
│     │  {                                                                     │
│     │    "id": 123,                                                          │
│     │    "title": "Laptop slow",                                             │
│     │    "troubleshooting_steps": "...",                                     │
│     │    "ai_analysis": "..."                                                │
│     │  }                                                                     │
│     │                                                                         │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                          DATABASE SCHEMA                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  TABLE: users                                                                 │
│  ┌────────────────┬──────────────┬─────────────────────────────────┐        │
│  │ id             │ INTEGER      │ Primary Key                      │        │
│  │ email          │ STRING       │ Unique, Indexed                  │        │
│  │ name           │ STRING       │ User's full name                 │        │
│  │ hashed_password│ STRING       │ Bcrypt hash                      │        │
│  │ role           │ STRING       │ Role enum value                  │        │
│  │ department     │ STRING       │ For team-based access            │        │
│  │ is_active      │ BOOLEAN      │ Account status                   │        │
│  │ created_at     │ DATETIME     │ Creation timestamp               │        │
│  │ updated_at     │ DATETIME     │ Last update                      │        │
│  └────────────────┴──────────────┴─────────────────────────────────┘        │
│                                                                               │
│  TABLE: tickets                                                               │
│  ┌────────────────┬──────────────┬─────────────────────────────────┐        │
│  │ id             │ INTEGER      │ Primary Key                      │        │
│  │ title          │ STRING       │ Ticket title                     │        │
│  │ description    │ TEXT         │ Issue description                │        │
│  │ status         │ ENUM         │ open, in_progress, resolved      │        │
│  │ priority       │ ENUM         │ low, medium, high, critical      │        │
│  │ user_email     │ STRING       │ Ticket owner                     │        │
│  │ assigned_to    │ STRING       │ Support agent                    │        │
│  │ created_at     │ DATETIME     │ Creation timestamp               │        │
│  └────────────────┴──────────────┴─────────────────────────────────┘        │
│                                                                               │
│  TABLE: audit_logs                                                            │
│  ┌────────────────┬──────────────┬─────────────────────────────────┐        │
│  │ id             │ INTEGER      │ Primary Key                      │        │
│  │ timestamp      │ DATETIME     │ When action occurred             │        │
│  │ user_id        │ STRING       │ User who performed action        │        │
│  │ user_email     │ STRING       │ User email                       │        │
│  │ user_role      │ STRING       │ User's role                      │        │
│  │ action         │ STRING       │ Action type                      │        │
│  │ resource_type  │ STRING       │ e.g., "ticket", "user"           │        │
│  │ resource_id    │ STRING       │ Resource identifier              │        │
│  │ success        │ STRING       │ success, failure, denied         │        │
│  │ details        │ TEXT         │ Human-readable description       │        │
│  │ metadata       │ JSON         │ Additional structured data       │        │
│  │ ip_address     │ STRING       │ Client IP                        │        │
│  └────────────────┴──────────────┴─────────────────────────────────┘        │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Layer 1: AUTHENTICATION                                                      │
│    • JWT tokens with expiration                                              │
│    • Bcrypt password hashing                                                 │
│    • Token verification on every request                                     │
│    • Invalid tokens rejected immediately                                     │
│                                                                               │
│  Layer 2: AUTHORIZATION (RBAC)                                                │
│    • Role-based permissions                                                  │
│    • Permission decorators on endpoints                                      │
│    • Automatic permission checking                                           │
│    • Deny by default, grant explicitly                                       │
│                                                                               │
│  Layer 3: RESOURCE-LEVEL ACCESS                                               │
│    • Check ticket ownership                                                  │
│    • Verify team membership                                                  │
│    • Filter query results by role                                            │
│    • Hide unauthorized data                                                  │
│                                                                               │
│  Layer 4: AUDIT LOGGING                                                       │
│    • All actions logged                                                      │
│    • Access denied events tracked                                            │
│    • Immutable audit trail                                                   │
│    • Searchable and filterable                                               │
│                                                                               │
│  Layer 5: DATA PRIVACY                                                        │
│    • Users see only authorized data                                          │
│    • Minimal PII in logs                                                     │
│    • Sensitive operations restricted                                         │
│    • No credential storage                                                   │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                     ROLE PERMISSION SUMMARY                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  STAFF (Regular Employee)                                                     │
│    ✅ View own tickets                                                        │
│    ✅ Create tickets                                                          │
│    ✅ Update own tickets                                                      │
│    ✅ View dashboard                                                          │
│    ✅ View knowledge base                                                     │
│    ❌ No admin operations                                                     │
│    ❌ No troubleshooting                                                      │
│                                                                               │
│  CONTRACTOR (External)                                                        │
│    ✅ View own tickets only                                                   │
│    ✅ Create tickets                                                          │
│    ✅ View knowledge base                                                     │
│    ❌ No team visibility                                                      │
│    ❌ No updates after creation                                               │
│    ❌ Highly restricted                                                       │
│                                                                               │
│  MANAGER (Team Lead)                                                          │
│    ✅ View team tickets                                                       │
│    ✅ View reports                                                            │
│    ✅ Escalate tickets                                                        │
│    ❌ Cannot troubleshoot                                                     │
│    ❌ Cannot manage users                                                     │
│                                                                               │
│  SUPPORT L1 (Basic Support)                                                   │
│    ✅ View all tickets                                                        │
│    ✅ Update any ticket                                                       │
│    ✅ Assign tickets                                                          │
│    ✅ Run troubleshooting                                                     │
│    ✅ Edit knowledge base                                                     │
│    ❌ Cannot delete tickets                                                   │
│    ❌ Cannot manage users                                                     │
│                                                                               │
│  SUPPORT L2 (Advanced Support)                                                │
│    ✅ All L1 permissions                                                      │
│    ✅ Delete tickets                                                          │
│    ✅ Auto-resolve issues                                                     │
│    ✅ System monitoring                                                       │
│    ✅ Export reports                                                          │
│    ❌ Cannot manage users                                                     │
│                                                                               │
│  SUPPORT L3 (Senior Engineer)                                                 │
│    ✅ All L2 permissions                                                      │
│    ✅ Manage users                                                            │
│    ❌ Cannot change roles                                                     │
│    ❌ Cannot view all audit logs                                              │
│                                                                               │
│  IT ADMIN (IT Operations)                                                     │
│    ✅ All L3 permissions                                                      │
│    ✅ Manage user roles                                                       │
│    ✅ System administration                                                   │
│    ❌ Cannot view all audit logs                                              │
│                                                                               │
│  SYSTEM ADMIN (Full Access)                                                   │
│    ✅ ALL PERMISSIONS                                                         │
│    ✅ View all audit logs                                                     │
│    ✅ System configuration                                                    │
│    ✅ Complete control                                                        │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                        IMPLEMENTATION STATUS                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ✅ COMPLETED                                                                 │
│     • 8 user roles defined                                                   │
│     • 20+ permissions implemented                                            │
│     • JWT authentication                                                     │
│     • RBAC middleware                                                        │
│     • Ticket access control                                                  │
│     • Audit logging system                                                   │
│     • User management API                                                    │
│     • Admin endpoints                                                        │
│     • Database models                                                        │
│     • Initialization script                                                  │
│     • Test suite                                                             │
│     • Complete documentation                                                 │
│                                                                               │
│  🔄 FRONTEND INTEGRATION (Next)                                               │
│     • Role-based UI rendering                                                │
│     • Permission checks                                                      │
│     • User management interface                                              │
│     • Audit log viewer                                                       │
│                                                                               │
│  ⭐ OPTIONAL ENHANCEMENTS                                                     │
│     • Multi-factor authentication                                            │
│     • Department-based teams                                                 │
│     • IP whitelisting                                                        │
│     • Session management                                                     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```
