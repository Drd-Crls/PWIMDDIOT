# SPEC.md - Contexts (IoT Grouping)

## Feature Goal
Enable creation and management of Contexts (logical groupings/domains) in the IoT system. Contexts serve as containers for sensors/devices with common characteristics or location.

## Requirements

### Functional Requirements
1. Create context with name (required) and optional description
2. List all contexts with pagination (page, limit) and optional name-based filtering
3. Retrieve a single context by UUID
4. Update context name and/or description
5. Delete context (physically from database)
6. Auto-manage timestamps (created_at, updated_at)
7. Return descriptive 404 when context not found

### Non-Functional Requirements
- Context ID auto-generated as UUID v4
- Name indexed for fast filtering
- Timestamps auto-set and auto-updated
- Pagination limited to 1-100 items per page
- Support filtering by name (case-insensitive substring match)
- Thread-safe database operations

## API Contract

### 1. Create Context
```
POST /contexts
Content-Type: application/json
```

**Request Schema**:
```json
{
  "name": "Sala de Sensoriamento A",
  "description": "Contexto para sensores da sala A do laboratório"
}
```

**Validation**:
- `name` (required, string): 1-100 chars, trimmed
- `description` (optional, string): any text

**Response Schema (Success - 201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Sala de Sensoriamento A",
  "description": "Contexto para sensores da sala A do laboratório",
  "created_at": "2026-04-28T10:30:00",
  "updated_at": "2026-04-28T10:30:00"
}
```

**Error Response (400 Bad Request - Empty Name)**:
```json
{
  "detail": "'name' is required and cannot be empty",
  "status": 400
}
```

---

### 2. List Contexts
```
GET /contexts?page=1&limit=10&name=Sala
```

**Query Parameters**:
- `page` (int, optional, default=1): Page number (1-based)
- `limit` (int, optional, default=10): Items per page (1-100)
- `name` (string, optional): Filter by name substring (case-insensitive)

**Response Schema (200 OK)**:
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Sala A",
      "description": "Sensors in room A",
      "created_at": "2026-04-28T10:30:00",
      "updated_at": "2026-04-28T10:30:00"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 10
}
```

**Error Response (400 Bad Request - Invalid Pagination)**:
```json
{
  "detail": "'limit' must be between 1 and 100",
  "status": 400
}
```

---

### 3. Get Context by ID
```
GET /contexts/{id}
```

**Response Schema (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Sala A",
  "description": "Sensors in room A",
  "created_at": "2026-04-28T10:30:00",
  "updated_at": "2026-04-28T10:30:00"
}
```

**Error Response (404 Not Found)**:
```json
{
  "detail": "Context not found",
  "status": 404
}
```

---

### 4. Update Context
```
PUT /contexts/{id}
Content-Type: application/json
```

**Request Schema** (all optional, but at least one should be provided):
```json
{
  "name": "Sala A - Updated",
  "description": "Updated description"
}
```

**Validation**:
- `name` (optional, string): 1-100 chars if provided
- `description` (optional, string): any text

**Response Schema (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Sala A - Updated",
  "description": "Updated description",
  "created_at": "2026-04-28T10:30:00",
  "updated_at": "2026-04-28T10:35:00"
}
```

**Error Response (404 Not Found)**:
```json
{
  "detail": "Context not found",
  "status": 404
}
```

---

### 5. Delete Context
```
DELETE /contexts/{id}
```

**Response (200 OK)**:
```json
{
  "detail": "Context deleted"
}
```

**Error Response (404 Not Found)**:
```json
{
  "detail": "Context not found",
  "status": 404
}
```

## Implementation Path

1. **Model** (`models/context.py`): UUID PK, name index, timestamps with onupdate
2. **Repository** (`repositories/context_repository.py`):
   - `get_by_id()` - fetch by UUID
   - `list()` - paginated query with name filtering
   - `create()` - insert and catch DB errors
   - `update()` - modify and refresh timestamps
   - `delete()` - remove (future: handle FK constraints)
3. **Service** (`services/context_service.py`):
   - Validate name (1-100 chars, trim)
   - Validate pagination (1-100 limit)
   - Raise `ValidationError` for invalid input
   - Raise `NotFoundError` for missing context
   - Delegate persistence to repository
4. **Controller** (`controllers/context_controller.py`): Orchestrate service methods
5. **Routes** (`routes/contexts.py`): REST endpoints with response models
6. **Container** (`core/container.py`): Dependency injection for repository/service/controller
7. **Main** (`main.py`): Register contexts router

## Security Considerations

- ✓ UUID for context ID (hard to enumerate)
- ✓ Name trimmed (prevents whitespace-only names)
- ✓ Pagination limits enforced (1-100 items max)
- ✓ Authentication required on `/contexts` endpoints via global `AuthMiddleware`; requests without the required auth header return `401 Unauthorized`
- ⏳ Authorization/role checks are not yet defined beyond authentication (future: require role-based access as needed)
- ⏳ No audit logging (future: log create/update/delete events)
- ⏳ No soft delete (future: add is_deleted flag for data retention)

## Edge Cases

| Case | Behavior |
|------|----------|
| Empty name | 400 ValidationError |
| Whitespace-only name | 400 ValidationError (trimmed to empty) |
| Name > 100 chars | 400 ValidationError |
| page < 1 | 400 ValidationError |
| limit > 100 | 400 ValidationError |
| Non-existent ID (GET/PUT/DELETE) | 404 NotFoundError |
| Database connection error | 500 DatabaseError |
| Empty filter results | 200 with items=[], total=0 |
| Special chars in name | Accepted (no sanitization beyond trim) |

## Dependencies

- `fastapi` - routing
- `sqlalchemy` - ORM + schema
- `pydantic` - validation + response model
- `dependency-injector` - DI container
- `psycopg2` or `psycopg2-binary` - PostgreSQL driver

## Configuration

| Setting | Source | Default | Purpose |
|---------|--------|---------|----------|
| `DATABASE_URL` | `.env` | (required) | Connect to PostgreSQL |
| Pagination limit | Code | 100 | Max items per page |
| Pagination default | Code | 10 | Default items if not specified |
