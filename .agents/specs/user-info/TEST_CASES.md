# TEST_CASES.md - Get Current User Info

## Test Coverage Matrix

| Scenario | Input | Expected | Status |
|----------|-------|----------|--------|
| Valid token | Bearer {valid_token} | 200, user object | ✅ Pass |
| Expired token | Bearer {expired_token} | 401 "Invalid or expired token" | ⏳ Verify |
| Tampered token | Bearer {modified_token} | 401 "Invalid or expired token" | ⏳ Verify |
| Invalid signature | Bearer {wrong_secret_signed} | 401 "Invalid or expired token" | ⏳ Verify |
| Missing Authorization header | (none) | 403 Forbidden | ✅ Pass |
| Wrong format (not Bearer) | "{token}" or "Basic ..." | 403 Forbidden | ⏳ Verify |
| User not found (token valid but user deleted) | Bearer {token_for_deleted_user} | 401 "User not found" | ⏳ Verify |

## Acceptance Criteria

- [ ] GET `/auth/me` with valid token returns user (200)
- [ ] Response includes id, name, email, role, created_at, updated_at
- [ ] Response excludes password field
- [ ] Missing Authorization header returns 403
- [ ] Invalid token returns 401 with generic message
- [ ] Expired token returns 401 with generic message
- [ ] Token signature validated with SECRET_KEY
- [ ] User lookup only happens after token validation
- [ ] Deleted user (token valid) returns 401 "User not found"
- [ ] Token claims correctly include `sub` (user_id) and `role`

## Manual Test Scenarios

### Scenario 1: Happy Path - Get Current User
**Precondition**: 
- User exists with email="alice@test.com"
- Valid token already obtained from `/auth/login`

```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Alice Johnson",
  "email": "alice@test.com",
  "role": "USER",
  "created_at": "2026-04-23T10:30:00",
  "updated_at": "2026-04-23T10:30:00"
}
```

**Verify**:
1. Status 200
2. User ID matches token `sub` claim
3. No password field
4. Timestamps present and valid

---

### Scenario 2: Missing Authorization Header
```bash
curl -X GET http://localhost:8000/auth/me
```

**Expected Response** (403 Forbidden):
```
403 Forbidden
```

---

### Scenario 3: Invalid Token (Tampered)
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...TAMPERED"
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Invalid or expired token"
}
```

---

### Scenario 4: Token Without Bearer Prefix
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: $TOKEN"
```

**Expected Response** (403 Forbidden - invalid scheme)

---

## Automated Test Template (pytest)

```python
# tests/auth/test_get_current_user.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.token_service import TokenService

client = TestClient(app)

@pytest.fixture
def valid_token(create_user):
    """Generate valid token for test user"""
    user = create_user(email="test@example.com")
    token_service = TokenService()
    return token_service.create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })

def test_get_current_user_success(valid_token):
    """Valid token returns user info"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "password" not in data
    assert data["email"] == "test@example.com"

def test_get_current_user_missing_header():
    """Missing Authorization header returns 403"""
    response = client.get("/auth/me")
    assert response.status_code == 403

def test_get_current_user_invalid_token():
    """Invalid token returns 401"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]

def test_get_current_user_wrong_bearer_scheme():
    """Non-Bearer Authorization returns 403"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Basic dGVzdDp0ZXN0"}
    )
    assert response.status_code == 403

def test_get_current_user_no_password_in_response(valid_token):
    """Response must not contain password"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200
    assert "password" not in response.json()
```

---

**Last Updated**: 2026-04-23
