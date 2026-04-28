# TEST_CASES.md - User Registration

## Test Coverage Matrix

| Scenario | Input | Expected | Status |
|----------|-------|----------|--------|
| Valid data | all fields correct | 201, user object | ✅ Pass |
| Duplicate email | email already exists | 409 Conflict | ✅ Pass |
| Missing name | {email, password, role} | 422 Validation Error | ✅ Pass |
| Missing email | {name, password, role} | 422 Validation Error | ✅ Pass |
| Missing password | {name, email, role} | 422 Validation Error | ✅ Pass |
| Missing role | {name, email, password} | 422 Validation Error | ✅ Pass |
| Invalid email format | email="not-an-email" | 422 Validation Error | ⏳ Verify |
| Invalid role | role="SUPERUSER" | 422 Validation Error | ✅ Pass |
| Empty name | name="" | Expected? | ❓ Ambiguous |
| Empty password | password="" | Expected? | ❓ Ambiguous |

## Acceptance Criteria

- [ ] POST `/users` with valid data creates user (201)
- [ ] User ID is UUID v4
- [ ] Password is hashed and not returned
- [ ] Email is unique (duplicate rejected with 409)
- [ ] Duplicate email message is descriptive
- [ ] Missing/invalid fields return 422
- [ ] Response excludes password field
- [ ] created_at/updated_at are auto-set
- [ ] Role enum validation enforced
- [ ] Email format validation enforced

## Manual Test Scenarios

### Scenario 1: Happy Path - Register New User
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Smith",
    "email": "bob@example.com",
    "password": "SecurePass123",
    "role": "USER"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Bob Smith",
  "email": "bob@example.com",
  "role": "USER",
  "created_at": "2026-04-23T10:30:00",
  "updated_at": "2026-04-23T10:30:00"
}
```

**Verify**:
1. Status 201
2. User ID is UUID format
3. created_at ≈ current time
4. No password in response

---

### Scenario 2: Duplicate Email
**Precondition**: User exists with email="alice@example.com"

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Another Alice",
    "email": "alice@example.com",
    "password": "DiffPassword123",
    "role": "USER"
  }'
```

**Expected Response** (409 Conflict):
```json
{
  "detail": "Email 'alice@example.com' already registered."
}
```

---

### Scenario 3: Missing Field (Email)
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Charlie Brown",
    "password": "password123",
    "role": "USER"
  }'
```

**Expected Response** (422):
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### Scenario 4: Invalid Role
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dave",
    "email": "dave@example.com",
    "password": "password123",
    "role": "SUPERADMIN"
  }'
```

**Expected Response** (422 - Invalid enum value)

---

## Automated Test Template (pytest)

```python
# tests/users/test_registration.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user_success(db):
    """Valid data creates user successfully"""
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "role": "USER"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "password" not in data
    assert "id" in data

def test_register_duplicate_email(db, create_user):
    """Duplicate email returns 409"""
    create_user(email="existing@example.com")
    response = client.post(
        "/users",
        json={
            "name": "Another User",
            "email": "existing@example.com",
            "password": "password123",
            "role": "USER"
        }
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]

def test_register_missing_email():
    """Missing email field returns 422"""
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "password": "password123",
            "role": "USER"
        }
    )
    assert response.status_code == 422

def test_register_invalid_role():
    """Invalid role value returns 422"""
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "role": "INVALID_ROLE"
        }
    )
    assert response.status_code == 422

def test_register_password_hashed(db):
    """Password is hashed in database"""
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "plaintext_password",
            "role": "USER"
        }
    )
    assert response.status_code == 201
    
    # Query database directly
    user = db.query(User).filter_by(email="test@example.com").first()
    assert user.password != "plaintext_password"  # Hashed
```

---

**Last Updated**: 2026-04-23
