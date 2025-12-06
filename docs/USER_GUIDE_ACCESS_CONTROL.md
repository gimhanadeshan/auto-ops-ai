# Quick Start Guide - Access Control & User Management

## 🚀 What Was Implemented

### New Pages Added

#### 1. **User Management** (`/users`)
![Admin Only]
- View and manage all system users
- Change user roles (8 different roles)
- Activate/deactivate user accounts
- Search and filter users
- Real-time permission preview

**Access:** IT Admin, System Admin

#### 2. **Audit Logs** (`/audit-logs`)
![All Users Can View Own Logs]
- Track all system activities
- View security events
- Export logs to CSV
- Monitor failed access attempts
- Filter by action, user, resource

**Access:** 
- All logs: System Admin only
- Own logs: All authenticated users

---

## 📍 How to Access

### For Admin Users:

1. **Login** to the system at `http://localhost:5173`
2. Look at the **sidebar navigation**
3. You'll see two new menu items with shield icons:
   - 🛡️ **User Management** 
   - 🛡️ **Audit Logs**
4. Click on either to access the features

### Navigation Location:
```
Sidebar Menu:
├── Dashboard
├── Quick Actions
├── AI Support Chat
├── Tickets
├── System Monitoring
├── Reports & Analytics
├── Automation Rules
├── Error Codes
├── Knowledge Base
├── 🛡️ User Management      ← NEW (Admin only)
├── 🛡️ Audit Logs           ← NEW (Admin only)
└── Settings
```

---

## 🔐 Role Permissions

### Who Can Do What?

| Feature | Staff | Contractor | Manager | Support L1 | Support L2 | Support L3 | IT Admin | System Admin |
|---------|-------|-----------|---------|------------|------------|------------|----------|--------------|
| View own audit logs | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View all users | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Change user roles | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Activate/deactivate users | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| View all audit logs | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Export audit logs | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🎯 Common Tasks

### Task 1: Change a User's Role
1. Go to **User Management**
2. Find the user (use search if needed)
3. Click the **Edit** button (pencil icon)
4. Select the new role from dropdown
5. Review the permissions list
6. Click **Update Role**

### Task 2: Deactivate a User
1. Go to **User Management**
2. Find the user
3. Click the **Deactivate** button (red X icon)
4. User will be immediately deactivated

### Task 3: View Your Activity
1. Go to **Audit Logs**
2. Click **My Logs** toggle
3. See all your actions with timestamps

### Task 4: Check Security Events
1. Go to **Audit Logs** (Admin only)
2. Look for the warning banner showing failed attempts
3. Use filters to investigate:
   - Filter by action: "ACCESS_DENIED"
   - Filter by user email
   - Export to CSV for analysis

### Task 5: Search Users
1. Go to **User Management**
2. Use the search box at the top
3. Type email or name
4. Results filter instantly

---

## 🎨 Visual Features

### User Management Page
```
┌────────────────────────────────────────┐
│  User Management                       │
│  Manage users, roles, and access       │
│                           [Refresh]    │
├────────────────────────────────────────┤
│ [Search...] [Role Filter] [Status]     │
├────────────────────────────────────────┤
│ User     Email         Role    Status  │
│ ─────────────────────────────────────  │
│ 👤 John  john@...     Admin   Active   │
│ 👤 Jane  jane@...     Staff   Active   │
│ 👤 Bob   bob@...      Manager Inactive │
└────────────────────────────────────────┘
```

### Audit Logs Page
```
┌────────────────────────────────────────┐
│  Audit Logs                            │
│  Track user actions and system events  │
│  [All Logs] [My Logs] [Export] [Refresh]
├────────────────────────────────────────┤
│ ⚠️ 3 failed access attempts (24h)      │
├────────────────────────────────────────┤
│ [Search...] [User] [Action] [Resource] │
├────────────────────────────────────────┤
│ ✅ USER_LOGIN                 5m ago    │
│    User: admin@acme.com                │
│    Details: Login successful           │
│                                        │
│ ⚠️ ACCESS_DENIED              15m ago  │
│    User: staff@acme.com                │
│    Details: Insufficient permissions   │
└────────────────────────────────────────┘
```

---

## 🔧 Technical Details

### Backend Endpoints (Already Working)
```
GET    /api/v1/admin/users
GET    /api/v1/admin/users/{id}
PUT    /api/v1/admin/users/{id}/role
PUT    /api/v1/admin/users/{id}/status
GET    /api/v1/admin/roles
GET    /api/v1/admin/audit-logs
GET    /api/v1/admin/audit-logs/me
GET    /api/v1/admin/audit-logs/failed-access
```

### Frontend Files Created
```
components/
  ├── UserManagement.jsx     ← User management UI
  └── AuditLogs.jsx          ← Audit logs UI

services/
  ├── userService.js         ← API calls for users
  └── auditService.js        ← API calls for logs

styles/components/
  ├── UserManagement.css     ← Styling
  └── AuditLogs.css          ← Styling
```

---

## ✅ Verification Checklist

Before using the features, verify:

- [x] Backend is running (http://localhost:8000)
- [x] Frontend is running (http://localhost:5173)
- [x] You can login with an admin account
- [x] Sidebar shows admin menu items with shield icons
- [x] No console errors in browser dev tools

---

## 🆘 Troubleshooting

### "Menu items not showing"
- **Cause:** Your account doesn't have admin role
- **Solution:** Login with IT Admin or System Admin account

### "401 Unauthorized error"
- **Cause:** Not logged in or token expired
- **Solution:** Logout and login again

### "403 Forbidden error"
- **Cause:** Your role doesn't have required permissions
- **Solution:** Contact system admin for role upgrade

### "Page not loading"
- **Cause:** Frontend server not running
- **Solution:** Run `npm run dev` in frontend folder

---

## 📊 Sample Data

### Test with these sample users (if in dev mode):
```
Admin Account:
  Email: admin@acme.com
  Password: [your admin password]
  
Staff Account:
  Email: staff@acme.com
  Password: [staff password]
```

### Sample Audit Log Actions:
- `USER_LOGIN` - User logged in
- `USER_LOGOUT` - User logged out
- `TICKET_CREATE` - New ticket created
- `TICKET_UPDATE` - Ticket modified
- `USER_ROLE_CHANGE` - Role changed
- `ACCESS_DENIED` - Permission denied

---

## 🎓 Best Practices

1. **Regular Monitoring:** Check audit logs daily for security
2. **Least Privilege:** Assign minimum required role
3. **Regular Reviews:** Review user access quarterly
4. **Export Logs:** Download logs monthly for compliance
5. **Track Failed Attempts:** Investigate repeated failures

---

**Everything is ready to use! Access the features through the sidebar.** 🎉
