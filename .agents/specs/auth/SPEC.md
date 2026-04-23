# SPEC.md - User Authentication (Login via JWT)

## Feature Goal
Enable users to log in with email and password, receiving a JWT token for subsequent API requests.

## Requirements

### Functional Requirements
1. Accept email and password in request body
2. Verify credentials against database
3. On success: issue JWT token with user identity and role
4. On failure: return 401 Unauthorized with message "Invalid email or password"
5. Token valid for 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
6. Token claims: `sub` (user_id as string), `role` (user's role enum value)

### Non-Functional Requirements
- Password verification must be constant-time (bcrypt with passlib)
- No plaintext passwords logged or returned
- Token signing uses HS256 algorithm
- Database queries optimized with email index
- Error messages consistent (never reveal if email exists or password wrong)

## API Contract

### Endpoint
```
POST /auth/login
Content-Type: application/json
```

### Request Schema
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Validation**:
- `email` (required, string): valid email format
- `password` (required, string): non-empty

### Response Schema (Success - 200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Error Response (401 Unauthorized)
```json
{
  "detail": "Invalid email or password"
}
```

## Implementation Path

1. **Route** (`routes/auth.py`): Accept POST, call controller
2. **Controller** (`controllers/auth_controller.py`): Orchestrate login via service
3. **Service** (`services/auth_service.py`):
   - Query user by email via repository
   - Verify password (bcrypt)
   - Generate JWT via `TokenService`
   - Return `TokenResponse` DTO
4. **Repository** (`repositories/user_repository.py`): Query by email
5. **Token Service** (`services/token_service.py`): Generate/sign JWT

## Security Considerations

- ❌ Never return "user not found" vs "password wrong"
- ✓ Always use bcrypt for password hashing
- ✓ Token signed with `SECRET_KEY` from environment
- ✓ Token expiry enforced at decode time
- ✓ Email queries use indexed column

## Edge Cases

| Case | Behavior |
|------|----------|
| Email not in database | 401 "Invalid email or password" |
| Password mismatch | 401 "Invalid email or password" |
| Malformed email | 422 Unprocessable Entity (Pydantic validation) |
| Missing email/password | 422 Unprocessable Entity (Pydantic validation) |
| Valid credentials | 200 OK with token |

## Dependencies

- `fastapi` - routing
- `sqlalchemy` - queries
- `pydantic` - validation
- `python-jose` - JWT signing
- `passlib + bcrypt` - password hashing
- `dependency-injector` - DI for repositories

## Configuration

| Setting | Source | Default | Purpose |
|---------|--------|---------|---------|
| `SECRET_KEY` | `.env` | (required) | JWT signing key |
| `ALGORITHM` | `.env` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `.env` | 30 | Token TTL |
| `DATABASE_URL` | `.env` | (required) | User queries |
