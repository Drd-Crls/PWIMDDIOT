# SPEC.md - Sensor Management (IoT Sensor CRUD)

## Feature Goal
Enable creation, retrieval, update, and deletion of sensors in the system. A Sensor represents a measurement channel (temperature, humidity, pressure, etc.) attached to a physical Device. A Device can expose multiple Sensors (1:N relationship).

## Requirements

### Functional Requirements
1. Create sensor with name, type, optional unit, optional min/max range, and required device_id
2. List all sensors with pagination (page, limit)
3. Support filtering by name, type, unit, and device_id
4. Support sorting by name, type, unit, device_id, created_at, updated_at
5. Retrieve a single sensor by UUID
6. Update sensor fields (name, type, unit, min_value, max_value, device_id)
7. Delete sensor from system
8. Auto-manage timestamps (created_at, updated_at)
9. Return descriptive 404 when sensor not found
10. Return 409 conflict when creating/updating a sensor with a non-existent device
11. Validate referenced device existence before persisting (prevent orphan relationships)

### Non-Functional Requirements
- Sensor ID auto-generated as UUID v4
- name, type, unit, device_id, created_at indexed for fast filtering and sorting
- Timestamps auto-set and auto-updated
- Pagination limited to 1-100 items per page
- Support case-insensitive filtering by name, type, and unit
- Foreign key constraint to devices prevents orphaned relationships
- Architecture prepared for future telemetry / real-time ingestion modules

## Domain Rules
- name required, max length: 128 characters
- type required, max length: 128 characters
- unit optional, max length: 64 characters
- min_value optional, numeric
- max_value optional, numeric
- When both min_value and max_value are provided, max_value must be >= min_value
- Sensors without min/max limits are allowed
- device_id required, must reference existing Device

### Sensor Type Convention
`type` is stored as a free-form string to keep the catalog open and extensible. Recommended canonical values:
- TEMPERATURE
- HUMIDITY
- PRESSURE
- VOLTAGE
- CURRENT
- FLOW
- LEVEL
- CUSTOM

Promoting `type` to an enum or lookup table is a deliberate future decision (see Future Considerations).

## API Contract

### 1. Create Sensor
```
POST /sensors
Content-Type: application/json
```

**Request Schema**:
```json
{
  "name": "Boiler Temperature",
  "type": "TEMPERATURE",
  "unit": "°C",
  "min_value": -10,
  "max_value": 120,
  "device_id": "770e8400-e29b-41d4-a716-446655440000"
}
```

**Validation**:
- `name` (required, string): 1-128 chars, trimmed
- `type` (required, string): 1-128 chars, trimmed
- `unit` (optional, string): max 64 chars
- `min_value` (optional, numeric)
- `max_value` (optional, numeric); when both present, must be >= min_value
- `device_id` (required, UUID): must reference existing Device

**Response Schema (Success - 201 Created)**:
```json
{
  "id": "9a0e8400-e29b-41d4-a716-446655440000",
  "name": "Boiler Temperature",
  "type": "TEMPERATURE",
  "unit": "°C",
  "min_value": -10,
  "max_value": 120,
  "device_id": "770e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-06-11T10:30:00",
  "updated_at": "2026-06-11T10:30:00"
}
```

**Error Responses**:
- 400: Required field missing/invalid, or max_value < min_value
- 409: Referenced device doesn't exist
- 422: Malformed UUID or wrong field types (Pydantic)

---

### 2. List Sensors
```
GET /sensors?page=1&limit=10&name=Boiler&type=TEMPERATURE&unit=%C2%B0C&device_id=xxx&sort_by=created_at&sort_order=desc
```

**Query Parameters**:
- `page` (int, optional, default=1): Page number (1-based)
- `limit` (int, optional, default=10): Items per page (1-100)
- `name` (string, optional): Filter by name substring (case-insensitive)
- `type` (string, optional): Filter by type substring (case-insensitive)
- `unit` (string, optional): Filter by unit substring (case-insensitive)
- `device_id` (UUID, optional): Filter by owning device
- `sort_by` (string, optional, default=created_at): name, type, unit, device_id, created_at, updated_at
- `sort_order` (string, optional, default=desc): asc or desc

**Response Schema (200 OK)**:
```json
{
  "items": [
    {
      "id": "9a0e8400-e29b-41d4-a716-446655440000",
      "name": "Boiler Temperature",
      "type": "TEMPERATURE",
      "unit": "°C",
      "min_value": -10,
      "max_value": 120,
      "device_id": "770e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-06-11T10:30:00",
      "updated_at": "2026-06-11T10:30:00"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 10
}
```

**Error Responses**:
- 400: Invalid pagination (limit > 100 or page < 1) or invalid sort_by column

---

### 3. Get Sensor
```
GET /sensors/{sensor_id}
```

**Response Schema (200 OK)**: same shape as create response.

**Error Response (404 Not Found)**:
```json
{
  "detail": "Sensor not found",
  "status": 404,
  "error_type": "not_found_error"
}
```

---

### 4. Update Sensor
```
PUT /sensors/{sensor_id}
Content-Type: application/json
```

**Request Schema** (all fields optional):
```json
{
  "name": "Boiler Temperature (Primary)",
  "type": "TEMPERATURE",
  "unit": "K",
  "min_value": 0,
  "max_value": 400,
  "device_id": "880e8400-e29b-41d4-a716-446655440000"
}
```

**Validation**:
- Same per-field rules as create, applied only to provided fields
- max_value >= min_value validated against the resulting (merged) state
- If device_id is provided, the new device must exist (else 409)

**Response Schema (200 OK)**: updated sensor; `updated_at` advanced.

**Error Responses**:
- 400: Validation error on provided fields (incl. range rule)
- 404: Sensor not found
- 409: New device_id references a non-existent device

---

### 5. Delete Sensor
```
DELETE /sensors/{sensor_id}
```

**Response Schema (200 OK)**:
```json
{
  "detail": "Sensor deleted"
}
```

**Error Responses**:
- 404: Sensor not found
- 409: Sensor still referenced by other entities (future relations)

## Database Schema

```sql
CREATE TABLE sensors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    type VARCHAR(128) NOT NULL,
    unit VARCHAR(64),
    min_value NUMERIC,
    max_value NUMERIC,
    device_id UUID NOT NULL REFERENCES devices(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_sensors_name ON sensors(name);
CREATE INDEX ix_sensors_type ON sensors(type);
CREATE INDEX ix_sensors_unit ON sensors(unit);
CREATE INDEX ix_sensors_device_id ON sensors(device_id);
CREATE INDEX ix_sensors_created_at ON sensors(created_at);
```

Migration file: `migrations/001_create_sensors_table.sql`. Tables are also auto-created at startup via `Base.metadata.create_all`.

## Architecture Decisions

### Clean Architecture Layers
- **Route Layer** (`routes/sensors.py`): HTTP entry points, no logic
- **Controller Layer** (`controllers/sensor_controller.py`): Request orchestration
- **Service Layer** (`services/sensor_service.py`): Business logic and validation
- **Repository Layer** (`repositories/sensor_repository.py`): Data access
- **Model Layer** (`models/sensor.py`): SQLAlchemy ORM entity + `device` relationship
- **Schema Layer** (`schemas/sensor.py`): Pydantic request/response DTOs

### Foreign Key Validation Strategy
- `SensorService` receives both `SensorRepositoryInterface` and `DeviceRepositoryInterface`
- Device existence is validated **proactively** before create/update, raising `ConflictError` (409) when the device is missing
- The repository additionally maps DB `IntegrityError` on `device_id` to `ConflictError` as a race-condition safety net
- This differs from the Device feature (which relies only on DB-level FK errors) and more strictly satisfies "validate device existence before persisting"

### Value Range Validation
- Enforced in two places: the Pydantic create DTO (`model_validator`) for request shape, and the service layer (authoritative) so partial updates that change only one bound are still validated against the merged state

### Numeric Representation
- `min_value` / `max_value` map to PostgreSQL `NUMERIC` and are represented as `Decimal` in DTOs to preserve precision

### Pagination / Filtering / Sorting
- 1-based pages, default limit 10, max 100, total count always returned
- Case-insensitive substring match for name/type/unit; exact UUID match for device_id; AND-combined
- Sort restricted to a safe column allowlist to prevent injection

## Future Considerations
- Promote `type` to an enum or lookup table once the catalog stabilizes
- Optional unique constraint on (device_id, name) if names must be unique per device
- Telemetry / readings relationship (new FK referencing sensors)
- Alerting rules based on min/max thresholds
- Cursor-based pagination for telemetry-scale reads
- Cascade strategy when a Device is deleted (currently RESTRICT via FK)
