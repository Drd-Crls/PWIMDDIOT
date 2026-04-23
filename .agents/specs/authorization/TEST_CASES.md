# TEST_CASES.md - Authorization & Role-Based Access Control

## Status
⏳ **Not yet implemented** - Infrastructure exists, tests define desired behavior

## Acceptance Criteria (to implement)

- [ ] ADMIN user can perform admin operations (e.g., delete user)
- [ ] USER user cannot perform admin operations (403 Forbidden)
- [ ] Permission denied message is generic (no enumeration)
- [ ] Role check happens before business logic
- [ ] Expired token cannot bypass authorization

## Test Scenarios (Template)

### Scenario 1: Admin Access Allowed
**Precondition**: User with role=ADMIN, valid token

```bash
TOKEN="eyJ... (admin role)"
curl -X DELETE http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**: 200/204 (operation succeeds)

---

### Scenario 2: User Denied Access
**Precondition**: User with role=USER, valid token

```bash
TOKEN="eyJ... (user role)"
curl -X DELETE http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**: 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### Scenario 3: No Token
```bash
curl -X DELETE http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000
```

**Expected**: 403 Forbidden

---

## Automated Test Template (pytest)

```python
# tests/auth/test_authorization.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def admin_token(create_user):
    """Token for ADMIN user"""
    from app.services.token_service import TokenService
    user = create_user(role="ADMIN")
    return TokenService.create_access_token({
        "sub": str(user.id),
        "role": "ADMIN"
    })

@pytest.fixture
def user_token(create_user):
    """Token for regular USER"""
    from app.services.token_service import TokenService
    user = create_user(role="USER")
    return TokenService.create_access_token({
        "sub": str(user.id),
        "role": "USER"
    })

def test_admin_can_delete_user(admin_token):
    """ADMIN role can perform deletion"""
    response = client.delete(
        "/users/550e8400-e29b-41d4-a716-446655440000",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # Expected: 200, 204, or 404 (if user not found)
    # NOT 403
    assert response.status_code != 403

def test_user_cannot_delete_user(user_token):
    """USER role denied deletion"""
    response = client.delete(
        "/users/550e8400-e29b-41d4-a716-446655440000",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_no_token_denied_deletion():
    """Unauthenticated request denied"""
    response = client.delete(
        "/users/550e8400-e29b-41d4-a716-446655440000"
    )
    assert response.status_code == 403
```

---

**Last Updated**: 2026-04-23
