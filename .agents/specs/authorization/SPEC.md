# SPEC.md - Authorization & Role-Based Access Control

## Feature Goal
Enable role-based access control (RBAC) for features, limiting which endpoints/operations only ADMIN users can perform.

## Current State

**Status**: 🟡 Partial Infrastructure, No Routes Using It

**Available**:
- `Role` enum in database model: ADMIN, USER
- `role` claim in JWT tokens
- `token_service.create_access_token()` includes role in payload
- User.role stored in database

**Missing**:
- Authorization decorators/middleware
- Role-checking logic in routes
- Admin-only endpoints documented
- Permission model defined

## Requirements (Draft)

### Functional Requirements
1. Define which operations require ADMIN role
2. Validate user role before allowing operation
3. Return 403 Forbidden if user lacks required role
4. Support granular permissions (per endpoint or per feature)

### Non-Functional Requirements
- Authorization check happens before business logic
- Error message consistent (no role enumeration)
- Performance: O(1) check (role already in token, no DB query)
- Scalable to future permission model (not just role-based)

## API Contract (Example)

### Protected Endpoint (Admin-Only)
```
DELETE /users/{user_id}
Authorization: Bearer {token_with_admin_role}
```

### Unauthorized Response (User Role)
```
403 Forbidden
```
```json
{
  "detail": "You do not have permission to perform this action."
}
```

## Implementation (Proposed)

### Option 1: Decorator Pattern
```python
from functools import wraps
from app.core.exceptions import ForbiddenError

def require_role(required_role: str):
    def decorator(func):
        async def wrapper(current_user: UserResponse = Depends(get_current_user), *args, **kwargs):
            if current_user.role != required_role:
                raise ForbiddenError("You do not have permission to perform this action.")
            return await func(current_user=current_user, *args, **kwargs)
        return wrapper
    return decorator

# Usage in route:
@router.delete("/users/{user_id}")
@require_role("ADMIN")
async def delete_user(user_id: UUID, current_user: UserResponse = Depends(get_current_user)):
    # Delete logic here
    pass
```

### Option 2: Middleware Pattern
```python
# Centralized middleware checks role from token claim
# Register in main.py
```

### Option 3: OpenAPI Security Schema
```python
# Integrate with FastAPI security schemes
# Automatic 403 response documentation
```

## Known Decisions Needed

| Decision | Option A | Option B | Notes |
|----------|----------|----------|-------|
| **Scope** | Per-endpoint | Per-feature | Per-endpoint is simpler but verbose |
| **Future** | Stick to ADMIN/USER | Add granular permissions | Affects table schema design |
| **Error** | Generic 403 | Detailed permission denied | Generic safer from security perspective |

## Dependencies

- `fastapi` - security/routing support
- Existing auth stack (JWT, role claims)

## Related Features

- Depends on: "User Authentication (Login)" - role claim in token
- Enables: Admin operations (delete user, manage roles, etc.)

## Future Work

- Define which endpoints are admin-only
- Implement authorization decorator/middleware
- Add permission management (RBAC evolution)
- Audit log (who did what, authorized or denied)
