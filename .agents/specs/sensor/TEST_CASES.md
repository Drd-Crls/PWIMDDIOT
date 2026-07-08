# TEST_CASES.md - Sensor Management Test Cases

## Test Coverage Matrix

| Layer | Component | Test Case | Status |
|-------|-----------|-----------|--------|
| Route | sensors.py | POST /sensors validates input | Not Yet |
| Route | sensors.py | GET /sensors pagination works | Not Yet |
| Route | sensors.py | GET /sensors filtering works | Not Yet |
| Route | sensors.py | GET /sensors/{id} returns sensor | Not Yet |
| Route | sensors.py | PUT /sensors/{id} updates sensor | Not Yet |
| Route | sensors.py | DELETE /sensors/{id} removes sensor | Not Yet |
| Controller | sensor_controller.py | create() orchestrates correctly | Not Yet |
| Controller | sensor_controller.py | list() passes params to service | Not Yet |
| Controller | sensor_controller.py | get() calls service and returns | Not Yet |
| Controller | sensor_controller.py | update() orchestrates correctly | Not Yet |
| Controller | sensor_controller.py | delete() calls service | Not Yet |
| Service | sensor_service.py | create_sensor validates name | Not Yet |
| Service | sensor_service.py | create_sensor validates type | Not Yet |
| Service | sensor_service.py | create_sensor validates unit length | Not Yet |
| Service | sensor_service.py | create_sensor enforces max>=min | Not Yet |
| Service | sensor_service.py | create_sensor raises on bad device_id | Not Yet |
| Service | sensor_service.py | list_sensors validates pagination | Not Yet |
| Service | sensor_service.py | list_sensors validates sort_by column | Not Yet |
| Service | sensor_service.py | list_sensors filters by name/type/unit | Not Yet |
| Service | sensor_service.py | list_sensors filters by device_id | Not Yet |
| Service | sensor_service.py | get_sensor raises NotFoundError | Not Yet |
| Service | sensor_service.py | update_sensor validates fields | Not Yet |
| Service | sensor_service.py | update_sensor revalidates range on merge | Not Yet |
| Service | sensor_service.py | update_sensor raises on bad device_id | Not Yet |
| Service | sensor_service.py | delete_sensor raises NotFoundError | Not Yet |
| Repository | sensor_repository.py | get_by_id returns sensor/None | Not Yet |
| Repository | sensor_repository.py | list() applies all filters | Not Yet |
| Repository | sensor_repository.py | list() returns count and items | Not Yet |
| Repository | sensor_repository.py | create() persists sensor | Not Yet |
| Repository | sensor_repository.py | create() maps FK IntegrityError to 409 | Not Yet |
| Repository | sensor_repository.py | update() updates sensor | Not Yet |
| Repository | sensor_repository.py | delete() removes sensor | Not Yet |

## Unit Test Cases

### Service Layer - Create Sensor

**TC_SENSOR_CREATE_001: Valid sensor creation**
- Input: Valid name, type, device_id (existing); no min/max
- Expected: Sensor created with auto-generated UUID and timestamps
- Assertion: Sensor.id is UUID, created_at == updated_at

**TC_SENSOR_CREATE_002: Empty name validation**
- Input: name = ""
- Expected: ValidationError raised
- Assertion: "name" in error message

**TC_SENSOR_CREATE_003: Name too long**
- Input: name = "x" * 129
- Expected: ValidationError raised
- Assertion: "128" in error message

**TC_SENSOR_CREATE_004: Empty type validation**
- Input: type = ""
- Expected: ValidationError raised
- Assertion: "type" in error message

**TC_SENSOR_CREATE_005: Unit too long**
- Input: unit = "x" * 65
- Expected: ValidationError raised
- Assertion: "64" in error message

**TC_SENSOR_CREATE_006: max_value < min_value**
- Input: min_value = 10, max_value = 5
- Expected: ValidationError (DTO and/or service)
- Assertion: "max_value" in error message

**TC_SENSOR_CREATE_007: Non-existent device_id**
- Input: device_id = UUID("00000000-0000-0000-0000-000000000000")
- Expected: ConflictError raised
- Assertion: "device" in error message

**TC_SENSOR_CREATE_008: No min/max provided (allowed)**
- Input: min_value = None, max_value = None
- Expected: Sensor created successfully
- Assertion: min_value is None and max_value is None

**TC_SENSOR_CREATE_009: Only min_value provided (allowed)**
- Input: min_value = 0, max_value = None
- Expected: Sensor created (range rule skipped when one side missing)
- Assertion: min_value == 0, max_value is None

**TC_SENSOR_CREATE_010: max_value == min_value (allowed)**
- Input: min_value = 5, max_value = 5
- Expected: Sensor created successfully
- Assertion: min_value == max_value

### Service Layer - List Sensors

**TC_SENSOR_LIST_001: Default pagination**
- Input: No params
- Expected: First 10 sensors sorted by created_at desc
- Assertion: items.length <= 10, total >= items.length

**TC_SENSOR_LIST_002: Invalid page < 1**
- Input: page = 0
- Expected: ValidationError raised
- Assertion: "page" in error message

**TC_SENSOR_LIST_003: Limit > 100**
- Input: limit = 101
- Expected: ValidationError raised
- Assertion: "limit" in error message

**TC_SENSOR_LIST_004: Invalid sort_by column**
- Input: sort_by = "; DROP TABLE"
- Expected: ValidationError raised
- Assertion: "sort_by" in error message

**TC_SENSOR_LIST_005: Filter by type**
- Input: type = "TEMP"
- Expected: Only sensors with "temp" in type (case-insensitive)
- Assertion: All items have "temp" in type.lower()

**TC_SENSOR_LIST_006: Filter by unit**
- Input: unit = "°C"
- Expected: Only sensors with that unit substring
- Assertion: All items contain the unit substring

**TC_SENSOR_LIST_007: Filter by device_id**
- Input: device_id = <uuid>
- Expected: Only sensors of that device
- Assertion: All items have device_id == <uuid>

**TC_SENSOR_LIST_008: Sorting by name ascending**
- Input: sort_by = "name", sort_order = "asc"
- Expected: Items sorted A-Z by name
- Assertion: items[i].name <= items[i+1].name

### Service Layer - Get Sensor

**TC_SENSOR_GET_001: Existing sensor**
- Input: sensor_id = <existing uuid>
- Expected: Sensor returned
- Assertion: sensor.id == sensor_id

**TC_SENSOR_GET_002: Non-existent sensor**
- Input: sensor_id = <non-existent uuid>
- Expected: NotFoundError raised
- Assertion: error_type == "not_found_error"

### Service Layer - Update Sensor

**TC_SENSOR_UPDATE_001: Update single field**
- Input: sensor_id, name = "Updated"
- Expected: Only name updated, updated_at advanced
- Assertion: sensor.name == "Updated", updated_at > created_at

**TC_SENSOR_UPDATE_002: Update min only, violates merged range**
- Prerequisite: Existing sensor with max_value = 5
- Input: min_value = 10
- Expected: ValidationError (merged max < min)
- Assertion: "max_value" in error message

**TC_SENSOR_UPDATE_003: Empty name update**
- Input: sensor_id, name = ""
- Expected: ValidationError raised
- Assertion: "name" in error message

**TC_SENSOR_UPDATE_004: Update non-existent sensor**
- Input: sensor_id = <non-existent uuid>
- Expected: NotFoundError raised
- Assertion: "not found" in error message

**TC_SENSOR_UPDATE_005: Reassign to non-existent device**
- Input: device_id = <non-existent uuid>
- Expected: ConflictError raised
- Assertion: "device" in error message

**TC_SENSOR_UPDATE_006: Reassign to existing device**
- Input: device_id = <existing uuid>
- Expected: Sensor reassigned
- Assertion: sensor.device_id == new device

### Service Layer - Delete Sensor

**TC_SENSOR_DELETE_001: Delete existing sensor**
- Input: sensor_id = <existing uuid>
- Expected: Sensor removed
- Assertion: get_sensor raises NotFoundError

**TC_SENSOR_DELETE_002: Delete non-existent sensor**
- Input: sensor_id = <non-existent uuid>
- Expected: NotFoundError raised
- Assertion: "not found" in error message

## Integration Test Cases

**TC_SENSOR_INT_001: Full CRUD workflow**
- Create device → Create sensor → Get sensor → Update sensor → List sensors → Delete sensor
- Assertions at each step

**TC_SENSOR_INT_002: Create with invalid device, then valid**
- Try create with bad device_id (409), then with valid device_id (201)
- Assertion: First raises ConflictError, second succeeds

**TC_SENSOR_INT_003: 1:N relationship**
- Create one device, create 3 sensors referencing it
- List sensors filtered by device_id
- Assertion: total == 3, all share device_id

**TC_SENSOR_INT_004: Pagination consistency**
- Create 25 sensors
- List page=1/2/3 with limit=10
- Assertion: Total = 25, no duplicates across pages

## Edge Cases

**TC_SENSOR_EDGE_001: Whitespace in name/type**
- Input: name = "  Boiler  ", type = "  TEMPERATURE  "
- Expected: Trimmed values persisted
- Assertion: sensor.name == "Boiler", sensor.type == "TEMPERATURE"

**TC_SENSOR_EDGE_002: Negative min and max**
- Input: min_value = -50, max_value = -10
- Expected: Created (−10 >= −50)
- Assertion: Values persisted correctly

**TC_SENSOR_EDGE_003: High-precision decimals**
- Input: min_value = 0.0001, max_value = 9999.9999
- Expected: Persisted without precision loss (NUMERIC/Decimal)
- Assertion: Returned values equal input

**TC_SENSOR_EDGE_004: Maximum length values**
- Input: name = "x"*128, type = "y"*128, unit = "z"*64
- Expected: All persisted correctly
- Assertion: All fields match input

## Error Handling Test Cases

**TC_SENSOR_ERROR_001: Malformed UUID in path**
- Input: sensor_id = "invalid-uuid"
- Expected: Pydantic validation error
- Assertion: HTTP 422 returned

**TC_SENSOR_ERROR_002: Malformed device_id in body**
- Input: device_id = "not-a-uuid"
- Expected: Pydantic validation error
- Assertion: HTTP 422 returned

**TC_SENSOR_ERROR_003: Missing required field**
- Input: Create request without type
- Expected: Pydantic validation error
- Assertion: HTTP 422 returned

**TC_SENSOR_ERROR_004: Database connection fails**
- Mock database error during create
- Expected: DatabaseError raised
- Assertion: HTTP 500 returned

## Security Test Cases

**TC_SENSOR_SEC_001: SQL injection in name filter**
- Input: name = "'; DROP TABLE sensors; --"
- Expected: Treated as literal string via ORM bind params
- Assertion: No injection, query succeeds

**TC_SENSOR_SEC_002: Sort column injection**
- Input: sort_by = "id); DROP TABLE sensors;--"
- Expected: Rejected by sort allowlist
- Assertion: ValidationError, no raw SQL executed

**TC_SENSOR_SEC_003: Auth required**
- Input: Request without Bearer token
- Expected: 401 from AuthMiddleware
- Assertion: HTTP 401 returned
