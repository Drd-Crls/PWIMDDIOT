# SPEC.md - User Registration

## Feature Goal
Enable new users to create an account with email, password, name, and assigned role.

## Requirements

### Functional Requirements
1. Accept email, password, name, and role in request body
2. Hash password using bcrypt
3. Store user in database
4. Return created user details (without password)
5. Reject duplicate email with 409 Conflict
6. Validate email format and password strength requirements

### Non-Functional Requirements
- Passwords hashed with bcrypt (never stored plaintext)
- Email uniqueness enforced at database level (unique constraint)
- Email indexed for fast lookups
- User ID auto-generated as UUID v4
- Timestamps (created_at, updated_at) auto-set
- Response excludes password field

## API Contract

### Endpoint
```
POST /users
Content-Type: application/json
```

### Request Schema
```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "password": "SecurePass123!",
  "role": "USER"
}
```

**Validation**:
- `name` (required, string): 1-255 chars
- `email` (required, string): valid email format, unique
- `password` (required, string): minimum 8 chars (inferred)
- `role` (required, enum): "USER" or "ADMIN"

### Response Schema (Success - 201 Created)
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

**Response Status**: 201 Created

### Error Response (409 Conflict - Duplicate Email)
```json
{
  "detail": "Email 'alice@example.com' already registered."
}
```

### Error Response (422 Unprocessable Entity - Validation)
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

## Implementation Path

1. **Route** (`routes/enroll.py`): Accept POST, call controller
2. **Controller** (`controllers/user_controller.py`): Orchestrate via service
3. **Service** (`services/user_service.py`):
   - Hash password via bcrypt
   - Create User model instance
   - Call repository to persist
   - Return `UserResponse` DTO
4. **Repository** (`repositories/user_repository.py`):
   - Attempt insert
   - Catch IntegrityError on duplicate email
   - Raise ConflictError with descriptive message
5. **Model** (`models/user.py`): Define schema with email unique + index

## Security Considerations

- ✓ Password hashed before storage
- ✓ Email uniqueness enforced (prevents duplicate accounts)
- ✓ No plaintext password in response
- ✓ UUID for user ID (hard to guess/enumerate)
- ❌ Password strength not enforced (future: add requirements)
- ❌ Email verification not implemented (account active on creation)

## Edge Cases

| Case | Behavior |
|------|----------|
| Duplicate email | 409 Conflict, descriptive message |
| Invalid email format | 422 Unprocessable Entity |
| Missing required field | 422 Unprocessable Entity |
| Empty name | 422 Unprocessable Entity (if validation applied) |
| Empty password | 422 Unprocessable Entity (if validation applied) |
| Invalid role value | 422 Unprocessable Entity |
| Valid data | 201 Created, user object returned |

## Dependencies

- `fastapi` - routing
- `sqlalchemy` - ORM + schema
- `pydantic` - validation + response model
- `passlib + bcrypt` - password hashing
- `dependency-injector` - DI

## Configuration

| Setting | Source | Default | Purpose |
|---------|--------|---------|---------|
| `DATABASE_URL` | `.env` | (required) | Persist user |
