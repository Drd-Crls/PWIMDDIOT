# SPEC.md - Device Management (IoT Device CRUD)

## Feature Goal
Enable creation, retrieval, update, and deletion of IoT devices in the system. Devices represent physical hardware connected to the network, organized within Contexts and created by Users.

## Requirements

### Functional Requirements
1. Create device with name, model, status, location, and required foreign keys
2. List all devices with pagination (page, limit)
3. Support filtering by name, model, status, and context_id
4. Support sorting by name, model, status, created_at, updated_at
5. Retrieve a single device by UUID
6. Update device fields (name, model, status, location)
7. Delete device from system
8. Auto-manage timestamps (created_at, updated_at)
9. Return descriptive 404 when device not found
10. Return 409 conflict when attempting to delete device still referenced by other entities
11. Return 409 conflict when creating device with non-existent context or user

### Non-Functional Requirements
- Device ID auto-generated as UUID v4
- Name indexed for fast filtering
- Timestamps auto-set and auto-updated
- Pagination limited to 1-100 items per page
- Support case-insensitive filtering by name and model
- Thread-safe database operations
- Foreign key constraints prevent orphaned relationships

## Domain Rules
- Status must be one of: ACTIVE, INACTIVE, MAINTENANCE, OFFLINE
- name max length: 128 characters
- model max length: 128 characters
- location max length: 256 characters (optional)
- context_id must reference existing Context
- created_by must reference existing User
- created_by is immutable after creation

## API Contract

### 1. Create Device
```
POST /devices
Content-Type: application/json
```

**Request Schema**:
```json
{
  "name": "Temperature Sensor A1",
  "model": "DHT22",
  "location": "Lab Building A, Room 101",
  "status": "ACTIVE",
  "context_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_by": "660e8400-e29b-41d4-a716-446655440000"
}
```

**Validation**:
- `name` (required, string): 1-128 chars, trimmed
- `model` (required, string): 1-128 chars, trimmed
- `location` (optional, string): max 256 chars
- `status` (required, enum): ACTIVE, INACTIVE, MAINTENANCE, OFFLINE
- `context_id` (required, UUID): must reference existing Context
- `created_by` (required, UUID): must reference existing User

**Response Schema (Success - 201 Created)**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "name": "Temperature Sensor A1",
  "model": "DHT22",
  "location": "Lab Building A, Room 101",
  "status": "ACTIVE",
  "context_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_by": "660e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-05-11T10:30:00",
  "updated_at": "2026-05-11T10:30:00"
}
```

**Error Responses**:
- 400: Required field missing or invalid
- 409: Referenced context or user doesn't exist

---

### 2. List Devices
```
GET /devices?page=1&limit=10&name=Temperature&status=ACTIVE&context_id=xxx&sort_by=created_at&sort_order=desc
```

**Query Parameters**:
- `page` (int, optional, default=1): Page number (1-based)
- `limit` (int, optional, default=10): Items per page (1-100)
- `name` (string, optional): Filter by name substring (case-insensitive)
- `model` (string, optional): Filter by model substring (case-insensitive)
- `status` (string, optional): Filter by status (ACTIVE, INACTIVE, MAINTENANCE, OFFLINE)
- `context_id` (UUID, optional): Filter by context
- `sort_by` (string, optional, default=created_at): Column to sort by
- `sort_order` (string, optional, default=desc): asc or desc

**Response Schema (200 OK)**:
```json
{
  "items": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "name": "Temperature Sensor A1",
      "model": "DHT22",
      "location": "Lab Building A, Room 101",
      "status": "ACTIVE",
      "context_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_by": "660e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-05-11T10:30:00",
      "updated_at": "2026-05-11T10:30:00"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 10
}
```

**Error Responses**:
- 400: Invalid pagination (limit > 100 or page < 1)

---

### 3. Get Device
```
GET /devices/{device_id}
```

**Response Schema (200 OK)**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "name": "Temperature Sensor A1",
  "model": "DHT22",
  "location": "Lab Building A, Room 101",
  "status": "ACTIVE",
  "context_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_by": "660e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-05-11T10:30:00",
  "updated_at": "2026-05-11T10:30:00"
}
```

**Error Response (404 Not Found)**:
```json
{
  "detail": "Device not found",
  "status": 404
}
```

---

### 4. Update Device
```
PUT /devices/{device_id}
Content-Type: application/json
```

**Request Schema** (all fields optional):
```json
{
  "name": "Updated Temperature Sensor A1",
  "model": "DHT22-PRO",
  "location": "Lab Building A, Room 102",
  "status": "MAINTENANCE"
}
```

**Validation**:
- `name` (optional): 1-128 chars if provided
- `model` (optional): 1-128 chars if provided
- `location` (optional): max 256 chars if provided
- `status` (optional): ACTIVE, INACTIVE, MAINTENANCE, OFFLINE if provided
- created_by cannot be updated

**Response Schema (200 OK)**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Temperature Sensor A1",
  "model": "DHT22-PRO",
  "location": "Lab Building A, Room 102",
  "status": "MAINTENANCE",
  "context_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_by": "660e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-05-11T10:30:00",
  "updated_at": "2026-05-11T10:30:45"
}
```

**Error Responses**:
- 400: Validation error on provided fields
- 404: Device not found

---

### 5. Delete Device
```
DELETE /devices/{device_id}
```

**Response Schema (200 OK)**:
```json
{
  "detail": "Device deleted"
}
```

**Error Responses**:
- 404: Device not found
- 409: Device still referenced by other entities

## Database Schema

```sql
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    model VARCHAR(128) NOT NULL,
    location VARCHAR(256),
    status VARCHAR(24) NOT NULL,
    context_id UUID NOT NULL REFERENCES contexts(id),
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_devices_name ON devices(name);
CREATE INDEX idx_devices_context_id ON devices(context_id);
CREATE INDEX idx_devices_created_by ON devices(created_by);
CREATE INDEX idx_devices_created_at ON devices(created_at);
```

## Architecture Decisions

### Clean Architecture Layers
- **Route Layer** (`routes/devices.py`): HTTP entry points, no logic
- **Controller Layer** (`controllers/device_controller.py`): Request orchestration
- **Service Layer** (`services/device_service.py`): Business logic and validation
- **Repository Layer** (`repositories/device_repository.py`): Data access with FK validation
- **Model Layer** (`models/device.py`): SQLAlchemy ORM entity
- **Schema Layer** (`schemas/device.py`): Pydantic request/response DTOs

### Foreign Key Validation Strategy
- Repository layer catches `IntegrityError` on FK constraint violations
- Converts to `ConflictError` for 409 response
- Service layer validates existence before operations when possible
- Future relationships will be prevented by FK constraints

### Pagination Strategy
- 1-based page numbers (user-friendly)
- Default limit 10, max 100 (configurable)
- Total count always returned for client-side pagination UI

### Filtering Strategy
- Case-insensitive substring matching for name and model
- Exact match for status enum
- UUID exact match for context_id
- Multiple filters combined with AND logic

### Sorting Strategy
- Default sort by created_at descending (newest first)
- Configurable sort column and direction
- Only allow safe sort columns (prevent injection)

## Future Considerations
- Multi-context device listing (may require authorization checks)
- Device metrics/telemetry relationships (will add FK references)
- Device notification rules (will add FK references)
- Batch device operations (create/update/delete multiple)
- Event streaming for device state changes
