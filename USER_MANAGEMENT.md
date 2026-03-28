# User and Role Management

## Overview

CogniData includes a comprehensive user management system with role-based access control (RBAC). This allows administrators to control who can access the application and what actions they can perform.

## User Roles

### 1. Admin
- **Full system access**
- Can manage users and assign roles
- Can create and manage backups
- Can view audit logs
- Can create, edit, and delete patients
- Can enter and delete tests
- Can generate reports and access dashboard

### 2. Practitioner
- **Default role for new users**
- Can create and edit patient records
- Can enter neuropsychological tests
- Can view tests and generate reports
- Can access the clinical dashboard
- **Cannot**: Manage users, delete data, create backups, or view audit logs

### 3. Viewer
- **Read-only access**
- Can view patient information
- Can view test results and dashboards
- Can view reports (but cannot generate)
- **Cannot**: Modify any data or access administrative features

## User Management Interface

Access user management via **Configuración → Gestión de Usuarios** (if you have Admin role).

### Three tabs are available:

#### Tab 1: Ver Usuarios (View Users)
- Displays a table of all registered users
- Shows: username, full name, role, active status, and creation date

#### Tab 2: Crear Usuario (Create User)
- Form to add a new user
- **Required fields**:
  - Username (min 3 characters, unique)
  - Password (min 6 characters)
  - Full Name
  - Role (Admin/Practitioner/Viewer)
  
#### Tab 3: Editar/Eliminar Usuario (Edit/Delete User)
- Select a user to modify
- **Edit section**:
  - Change full name
  - Change user role
- **Password section**:
  - Reset user password
  - Requires confirmation
- **Delete section**:
  - Permanently remove a user account

## Default Admin Account

When CogniData is first set up, a default admin account is created:

```
Username: admin
Password: admin123
Role: Administrator
```

⚠️ **IMPORTANT**: Change this password immediately after first login for security!

## Password Security

- Passwords are hashed using bcrypt with salt
- Minimum 6 characters required
- Passwords are never stored in plain text
- Each user can have their password changed by an admin or by themselves (if implemented)

## Permission Matrix

| Permission | Admin | Practitioner | Viewer |
|-----------|-------|--------------|--------|
| View Patients | ✅ | ✅ | ✅ |
| Create Patient | ✅ | ✅ | ❌ |
| Edit Patient | ✅ | ✅ | ❌ |
| Delete Patient | ✅ | ❌ | ❌ |
| Enter Tests | ✅ | ✅ | ❌ |
| View Tests | ✅ | ✅ | ✅ |
| Delete Tests | ✅ | ❌ | ❌ |
| Generate Reports | ✅ | ✅ | ❌ |
| View Dashboard | ✅ | ✅ | ✅ |
| Manage Users | ✅ | ❌ | ❌ |
| View Audit Logs | ✅ | ❌ | ❌ |
| Create Backups | ✅ | ❌ | ❌ |

## Best Practices

1. **Create role-specific accounts**: Don't share accounts; create individual accounts for each person
2. **Change default password**: Always change the default admin password immediately
3. **Use strong passwords**: Enforce strong password policies for admin accounts
4. **Regular audits**: Periodically review who has access and their roles
5. **Least privilege**: Assign users the minimum role required for their duties
6. **Audit logging**: Admins can review audit logs to track user actions

## Technical Details

### Database Schema

Users are stored in the `users` table with the following fields:
- `username` (String, unique primary key)
- `password_hash` (String, bcrypt hashed)
- `full_name` (String, optional)
- `role` (Enum: Admin, Practitioner, Viewer)
- `is_active` (Boolean, soft delete support)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### API/Service Functions

User management is implemented in `services/user_service.py`:

```python
# Create a user
create_user(username: str, password: str, full_name: str, role: UserRole) -> User

# Get all users
get_all_users() -> list[User]

# Update user details
update_user(username: str, full_name: str = None, role: UserRole = None) -> User

# Change password
change_password(username: str, new_password: str) -> bool

# Delete user
delete_user(username: str) -> bool

# Authenticate (for future login implementation)
authenticate_user(username: str, password: str) -> User | None
```

## Future Enhancements

- [ ] User login page with session management
- [ ] User profile page (change own password)
- [ ] Activity logging per user
- [ ] User deactivation (soft delete) instead of hard delete
- [ ] Multi-factor authentication (MFA)
- [ ] Password expiration policies
- [ ] Single sign-on (SSO) integration
