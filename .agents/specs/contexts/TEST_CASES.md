# TEST_CASES.md - Contexts

## Test Coverage Matrix

| Scenario | Input | Expected | Status |
|----------|-------|----------|--------|
| Valid create | {name: "Sala A"} | 201, context object | ✅ Pass |
| Valid create with description | {name: "Sala A", description: "..."} | 201, full object | ✅ Pass |
| Create with empty name | {name: ""} | 400 ValidationError | ✅ Pass |
| Create with whitespace name | {name: "   "} | 400 ValidationError | ✅ Pass |
| Create name too long | {name: "a" * 101} | 400 ValidationError | ✅ Pass |
| List with valid pagination | page=1, limit=10 | 200, items list | ✅ Pass |
| List with invalid limit | limit=101 | 400 ValidationError | ✅ Pass |
| List with page < 1 | page=0 | 400 ValidationError | ✅ Pass |
| List with name filter | name="Sala" | 200, filtered items | ✅ Pass |
| Get existing context | id=valid-uuid | 200, context object | ✅ Pass |
| Get non-existent context | id=invalid-uuid | 404 NotFoundError | ✅ Pass |
| Update name only | {name: "New Name"} | 200, updated object | ✅ Pass |
| Update description only | {description: "New desc"} | 200, updated object | ✅ Pass |
| Update both fields | {name: "...", description: "..."} | 200, updated object | ✅ Pass |
| Update non-existent | id=invalid-uuid | 404 NotFoundError | ✅ Pass |
| Delete existing context | id=valid-uuid | 200, deleted message | ✅ Pass |
| Delete non-existent context | id=invalid-uuid | 404 NotFoundError | ✅ Pass |

## Acceptance Criteria

- [ ] POST `/contexts` with valid name creates context (201)
- [ ] Context ID is UUID v4
- [ ] created_at/updated_at are auto-set
- [ ] Empty/whitespace name rejected (400)
- [ ] Name > 100 chars rejected (400)
- [ ] GET `/contexts` lists with pagination and filtering
- [ ] Pagination limit enforced (1-100)
- [ ] Name filter is case-insensitive substring match
- [ ] GET `/contexts/{id}` returns context or 404
- [ ] PUT `/contexts/{id}` updates and changes updated_at
- [ ] DELETE `/contexts/{id}` removes and returns 200
- [ ] Non-existent context returns 404 (GET/PUT/DELETE)
- [ ] List response includes `total` count
- [ ] Responses match ContextResponse schema

## Manual Test Scenarios

### Scenario 1: Happy Path - Create Context
```bash
curl -X POST http://localhost:8000/contexts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sala de Sensoriamento A",
    "description": "Contexto para sensores da sala A"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Sala de Sensoriamento A",
  "description": "Contexto para sensores da sala A",
  "created_at": "2026-04-28T10:30:00",
  "updated_at": "2026-04-28T10:30:00"
}
```

**Verify**:
1. Status 201
2. Context ID is UUID format
3. created_at ≈ current time
4. updated_at == created_at

---

### Scenario 2: Empty Name Validation
```bash
curl -X POST http://localhost:8000/contexts \
  -H "Content-Type: application/json" \
  -d '{"name": ""}'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": "'name' is required and cannot be empty",
  "status": 400
}
```

---

### Scenario 3: List with Pagination
```bash
curl http://localhost:8000/contexts?page=1&limit=5
```

**Expected Response** (200 OK):
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Sala A",
      "description": "...",
      "created_at": "2026-04-28T10:30:00",
      "updated_at": "2026-04-28T10:30:00"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 5
}
```

**Verify**:
1. Status 200
2. items array length ≤ 5
3. total reflects all contexts (42)

---

### Scenario 4: Filter by Name
```bash
curl http://localhost:8000/contexts?page=1&limit=10&name=Sala
```

**Expected Response** (200 OK):
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Sala A",
      ...
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Sala de Conferência",
      ...
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 10
}
```

**Verify**:
1. Only items with "Sala" in name are returned
2. Filter is case-insensitive
3. total reflects filtered count

---

### Scenario 5: Get Context by ID
```bash
curl http://localhost:8000/contexts/550e8400-e29b-41d4-a716-446655440000
```

**Expected Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Sala A",
  "description": "...",
  "created_at": "2026-04-28T10:30:00",
  "updated_at": "2026-04-28T10:30:00"
}
```

---

### Scenario 6: Get Non-Existent Context
```bash
curl http://localhost:8000/contexts/ffffffff-ffff-ffff-ffff-ffffffffffff
```

**Expected Response** (404 Not Found):
```json
{
  "detail": "Context not found",
  "status": 404
}
```

---

### Scenario 7: Update Context
```bash
curl -X PUT http://localhost:8000/contexts/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sala A - Atualizada",
    "description": "Nova descrição"
  }'
```

**Expected Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Sala A - Atualizada",
  "description": "Nova descrição",
  "created_at": "2026-04-28T10:30:00",
  "updated_at": "2026-04-28T10:35:00"
}
```

**Verify**:
1. Name changed
2. updated_at is newer than created_at
3. created_at unchanged

---

### Scenario 8: Delete Context
```bash
curl -X DELETE http://localhost:8000/contexts/550e8400-e29b-41d4-a716-446655440000
```

**Expected Response** (200 OK):
```json
{
  "detail": "Context deleted"
}
```

**Verify**:
1. Status 200
2. Subsequent GET returns 404

---

## Automated Tests (Suggested)

- Unit tests for `ContextService` (validation, business logic)
- Integration tests for `ContextRepository` (DB operations)
- Endpoint tests using `TestClient` with test database (separate PG schema or SQLite)
