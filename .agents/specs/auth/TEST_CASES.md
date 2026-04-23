# TEST_CASES.md - User Authentication (Login)

## Test Coverage Matrix

| Scenario | Input | Expected | Status |
|----------|-------|----------|--------|
| Valid credentials | email=existing@test.com, password=correct | 200, access_token issued | ✅ Pass |
| Invalid password | email=existing@test.com, password=wrong | 401 "Invalid email or password" | ✅ Pass |
| Email not found | email=nonexistent@test.com, password=any | 401 "Invalid email or password" | ✅ Pass |
| Missing email | {password: "..."} | 422 Unprocessable Entity | ✅ Pass |
| Missing password | {email: "..."} | 422 Unprocessable Entity | ✅ Pass |
| Malformed email | email="not-an-email", password="..." | 422 Unprocessable Entity | ❌ Need to verify |
| Empty password | email="test@test.com", password="" | Expected behavior? | ❓ Ambiguous |

## Acceptance Criteria

- [ ] POST `/auth/login` with valid credentials returns JWT token
- [ ] Token type is "bearer"
- [ ] Token payload contains `sub` (user_id) and `role` claims
- [ ] Token signature validates with SECRET_KEY
- [ ] Token expires after configured minutes
- [ ] Invalid password returns 401 with generic message
- [ ] Non-existent email returns 401 with generic message
- [ ] Missing/invalid fields return 422 validation error
- [ ] Password verification is constant-time (no timing attacks)
- [ ] No plaintext password in logs or response

## Manual Test Scenarios

### Scenario 1: Happy Path
**Precondition**: User exists with email="alice@test.com", password_hash=hash("password123"), role=USER

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"password123"}'
```

**Expected Response**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Verify**:
1. Response status 200
2. `access_token` is non-empty string
3. Token decodes with `token_service.decode_token()`
4. Payload has `sub` and `role` keys

---

### Scenario 2: Wrong Password
**Precondition**: Same user as above

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"wrongpassword"}'
```

**Expected Response**: 401 Unauthorized
```json
{
  "detail": "Invalid email or password"
}
```

---

### Scenario 3: Email Not Found
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"nothere@test.com","password":"anything"}'
```

**Expected Response**: 401 Unauthorized (same message as wrong password)

---

### Scenario 4: Missing Fields
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com"}'
```

**Expected Response**: 422 Unprocessable Entity (field validation error)

---

## Automated Test Template (pytest)

```python
# tests/auth/test_login.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_valid_credentials(setup_user):
    """Valid email and password returns token"""
    response = client.post(
        "/auth/login",
        json={"email": "test@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_password(setup_user):
    """Wrong password returns 401"""
    response = client.post(
        "/auth/login",
        json={"email": "test@test.com", "password": "wrongpwd"}
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_login_email_not_found():
    """Non-existent email returns 401"""
    response = client.post(
        "/auth/login",
        json={"email": "notfound@test.com", "password": "anything"}
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_login_missing_email():
    """Missing email field returns 422"""
    response = client.post(
        "/auth/login",
        json={"password": "password123"}
    )
    assert response.status_code == 422

def test_login_missing_password():
    """Missing password field returns 422"""
    response = client.post(
        "/auth/login",
        json={"email": "test@test.com"}
    )
    assert response.status_code == 422
```

## Performance Benchmarks

| Test | Target | Current | Status |
|------|--------|---------|--------|
| Login response time | <200ms | ? | ⏳ Measure |
| Password verification time | constant ~100-150ms | ? | ⏳ Measure |
| Database query (email index) | <10ms | ? | ⏳ Measure |

---

**Last Updated**: 2026-04-23
