# SPEC.md - Get Current User Info

## Feature Goal
Enable authenticated users to retrieve their own profile information via JWT token.

## Requirements

### Functional Requirements
1. Accept JWT token in Authorization header (Bearer scheme)
2. Validate and decode token
3. Extract user_id from token claim (`sub`)
4. Query user from database
5. Return user details (excluding password)
6. Reject invalid/expired tokens with 401 Unauthorized

### Non-Functional Requirements
- Token validation is fast (no extra DB queries for validation)
- Token must not be expired
- User lookup happens only after token validation
- Error messages consistent (generic, no user enumeration)
- Response includes all user fields except password

## API Contract

### Endpoint
```
GET /auth/me
Authorization: Bearer {token}
```

### Request
- No body
- Header required: `Authorization: Bearer eyJ...`

### Response Schema (Success - 200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "role": "USER",
  "created_at": "2026-04-23T10:30:00",
  "updated_at": "2026-04-23T10:30:00"
}
```

### Error Response (401 Unauthorized - Missing Token)
```
401 Unauthorized
WWW-Authenticate: Bearer
```
```json
{
  "detail": "Not authenticated"
}
```

### Error Response (401 Unauthorized - Invalid Token)
```json
{
  "detail": "Invalid or expired token"
}
```

### Error Response (401 Unauthorized - User Not Found)
```json
{
  "detail": "User not found"
}
```

## Implementation Path

1. **Route** (`routes/auth.py`): GET endpoint with HTTPBearer dependency
2. **Dependency** (`core/dependencies.py`):
   - Extract token from Authorization header
   - Decode JWT and validate claims
   - Query user by `sub` (user_id)
   - Return `UserResponse` DTO or raise UnauthorizedError
3. **Token Service** (`services/token_service.py`): Decode and validate JWT
4. **Repository** (`repositories/user_repository.py`): Query by UUID

## Security Considerations

- ✓ HTTPBearer scheme enforces "Bearer {token}" format
- ✓ Token signature validated before accepting claims
- ✓ Token expiry checked at decode time
- ✓ User lookup happens after token validation (fail-safe)
- ✓ Password never returned in response
- ✓ No user enumeration attacks (consistent error message)

## Edge Cases

| Case | Behavior |
|------|----------|
| No Authorization header | 403 Forbidden (FastAPI HTTPBearer default) |
| Malformed Authorization header | 403 Forbidden |
| Invalid/tampered token | 401 "Invalid or expired token" |
| Expired token | 401 "Invalid or expired token" |
| User deleted after token issued | 401 "User not found" |
| Valid token | 200 OK with user object |

## Dependencies

- `fastapi` - routing
- `fastapi.security.HTTPBearer` - token extraction
- `sqlalchemy` - user query
- `python-jose` - JWT decode
- `dependency-injector` - DI

## Configuration

| Setting | Source | Default | Purpose |
|---------|--------|---------|---------|
| `SECRET_KEY` | `.env` | (required) | JWT verification |
| `ALGORITHM` | `.env` | HS256 | JWT algorithm |
| `DATABASE_URL` | `.env` | (required) | User lookup |

## Related Features

- Depends on: "User Authentication (Login)" - token must be valid
- Used by: Any authenticated endpoint as reference implementation
