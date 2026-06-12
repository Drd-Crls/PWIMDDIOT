# TEST_CASES.md - Device Management Test Cases

## Test Coverage Matrix

| Layer | Component | Test Case | Status |
|-------|-----------|-----------|--------|
| Route | devices.py | POST /devices validates input | Not Yet |
| Route | devices.py | GET /devices pagination works | Not Yet |
| Route | devices.py | GET /devices filtering works | Not Yet |
| Route | devices.py | GET /devices/{id} returns device | Not Yet |
| Route | devices.py | PUT /devices/{id} updates device | Not Yet |
| Route | devices.py | DELETE /devices/{id} removes device | Not Yet |
| Controller | device_controller.py | create() orchestrates correctly | Not Yet |
| Controller | device_controller.py | list() passes params to service | Not Yet |
| Controller | device_controller.py | get() calls service and returns | Not Yet |
| Controller | device_controller.py | update() orchestrates correctly | Not Yet |
| Controller | device_controller.py | delete() calls service | Not Yet |
| Service | device_service.py | create_device validates name | Not Yet |
| Service | device_service.py | create_device validates model | Not Yet |
| Service | device_service.py | create_device validates status enum | Not Yet |
| Service | device_service.py | create_device raises on bad context_id | Not Yet |
| Service | device_service.py | create_device raises on bad created_by | Not Yet |
| Service | device_service.py | list_devices validates pagination | Not Yet |
| Service | device_service.py | list_devices filters by name | Not Yet |
| Service | device_service.py | list_devices filters by model | Not Yet |
| Service | device_service.py | list_devices filters by status | Not Yet |
| Service | device_service.py | list_devices filters by context_id | Not Yet |
| Service | device_service.py | list_devices sorts correctly | Not Yet |
| Service | device_service.py | get_device returns device | Not Yet |
| Service | device_service.py | get_device raises NotFoundError | Not Yet |
| Service | device_service.py | update_device validates fields | Not Yet |
| Service | device_service.py | update_device updates updated_at | Not Yet |
| Service | device_service.py | delete_device raises on FK conflict | Not Yet |
| Repository | device_repository.py | get_by_id returns device | Not Yet |
| Repository | device_repository.py | get_by_id returns None | Not Yet |
| Repository | device_repository.py | list() applies all filters | Not Yet |
| Repository | device_repository.py | list() returns count and items | Not Yet |
| Repository | device_repository.py | create() persists device | Not Yet |
| Repository | device_repository.py | create() raises on FK constraint | Not Yet |
| Repository | device_repository.py | update() updates device | Not Yet |
| Repository | device_repository.py | delete() removes device | Not Yet |
| Repository | device_repository.py | delete() raises on FK constraint | Not Yet |

## Unit Test Cases

### Service Layer - Create Device

**TC_DEVICE_CREATE_001: Valid device creation**
- Input: Valid name, model, status, context_id, created_by
- Expected: Device created with auto-generated UUID and timestamps
- Assertion: Device.id is UUID, created_at == updated_at

**TC_DEVICE_CREATE_002: Empty name validation**
- Input: name = ""
- Expected: ValidationError raised
- Assertion: "name" in error message

**TC_DEVICE_CREATE_003: Name too long**
- Input: name = "x" * 129
- Expected: ValidationError raised
- Assertion: "128" in error message

**TC_DEVICE_CREATE_004: Empty model validation**
- Input: model = ""
- Expected: ValidationError raised
- Assertion: "model" in error message

**TC_DEVICE_CREATE_005: Non-existent context_id**
- Input: context_id = UUID("00000000-0000-0000-0000-000000000000")
- Expected: ConflictError raised
- Assertion: "context" in error message

**TC_DEVICE_CREATE_006: Non-existent created_by**
- Input: created_by = UUID("00000000-0000-0000-0000-000000000000")
- Expected: ConflictError raised
- Assertion: "user" in error message

**TC_DEVICE_CREATE_007: Location too long**
- Input: location = "x" * 257
- Expected: ValidationError raised
- Assertion: "256" in error message

**TC_DEVICE_CREATE_008: Invalid status enum**
- Input: status = "INVALID"
- Expected: Pydantic validation error at route level
- Assertion: 422 status code

### Service Layer - List Devices

**TC_DEVICE_LIST_001: Default pagination**
- Input: No params
- Expected: First 10 devices sorted by created_at desc
- Assertion: items.length <= 10, total >= items.length

**TC_DEVICE_LIST_002: Custom page and limit**
- Input: page=2, limit=5
- Expected: Items 6-10
- Assertion: items.length <= 5

**TC_DEVICE_LIST_003: Invalid page < 1**
- Input: page=0
- Expected: ValidationError raised
- Assertion: "page" in error message

**TC_DEVICE_LIST_004: Limit > 100**
- Input: limit=101
- Expected: ValidationError raised
- Assertion: "limit" in error message

**TC_DEVICE_LIST_005: Filter by name substring**
- Input: name="Temp"
- Expected: Only devices with "Temp" in name
- Assertion: All items have "temp" in name.lower()

**TC_DEVICE_LIST_006: Filter by model**
- Input: model="DHT"
- Expected: Only devices with "DHT" in model
- Assertion: All items have "dht" in model.lower()

**TC_DEVICE_LIST_007: Filter by status**
- Input: status="ACTIVE"
- Expected: Only active devices
- Assertion: All items have status == ACTIVE

**TC_DEVICE_LIST_008: Filter by context_id**
- Input: context_id=<uuid>
- Expected: Only devices in that context
- Assertion: All items have context_id == <uuid>

**TC_DEVICE_LIST_009: Sorting by name ascending**
- Input: sort_by="name", sort_order="asc"
- Expected: Items sorted A-Z by name
- Assertion: items[i].name <= items[i+1].name for all i

**TC_DEVICE_LIST_010: Sorting by created_at descending**
- Input: sort_by="created_at", sort_order="desc"
- Expected: Items sorted newest first
- Assertion: items[i].created_at >= items[i+1].created_at for all i

### Service Layer - Get Device

**TC_DEVICE_GET_001: Existing device**
- Input: device_id = <existing uuid>
- Expected: Device returned
- Assertion: device.id == device_id

**TC_DEVICE_GET_002: Non-existent device**
- Input: device_id = <non-existent uuid>
- Expected: NotFoundError raised
- Assertion: error_type == "not_found_error"

### Service Layer - Update Device

**TC_DEVICE_UPDATE_001: Update single field**
- Input: device_id, name="Updated"
- Expected: Only name updated, other fields unchanged
- Assertion: device.name == "Updated", updated_at > created_at

**TC_DEVICE_UPDATE_002: Update multiple fields**
- Input: device_id, name="New", status="MAINTENANCE"
- Expected: Both fields updated
- Assertion: device.name == "New" and device.status == MAINTENANCE

**TC_DEVICE_UPDATE_003: Empty name update**
- Input: device_id, name=""
- Expected: ValidationError raised
- Assertion: "name" in error message

**TC_DEVICE_UPDATE_004: Update non-existent device**
- Input: device_id = <non-existent uuid>
- Expected: NotFoundError raised
- Assertion: "not found" in error message

**TC_DEVICE_UPDATE_005: Update location to null**
- Input: device_id, location=None
- Expected: Location unchanged
- Assertion: device.location == original_location

### Service Layer - Delete Device

**TC_DEVICE_DELETE_001: Delete existing device**
- Input: device_id = <existing uuid>
- Expected: Device removed
- Assertion: get_device raises NotFoundError

**TC_DEVICE_DELETE_002: Delete non-existent device**
- Input: device_id = <non-existent uuid>
- Expected: NotFoundError raised
- Assertion: "not found" in error message

**TC_DEVICE_DELETE_003: Delete device with future relationships**
- Prerequisite: Add FK constraint from another table to devices
- Input: device_id = <device referenced by another entity>
- Expected: ConflictError raised
- Assertion: "referenced" in error message

## Integration Test Cases

**TC_DEVICE_INT_001: Full CRUD workflow**
- Create device → Get device → Update device → List devices → Delete device
- Assertions at each step

**TC_DEVICE_INT_002: Create with invalid FK, then valid**
- Try create with bad context_id (fails)
- Try again with valid context_id (succeeds)
- Assertions: First raises ConflictError, second succeeds

**TC_DEVICE_INT_003: List with combined filters**
- Create multiple devices in different contexts
- List with name + status filters
- Assertion: Only matching devices returned

**TC_DEVICE_INT_004: Pagination consistency**
- Create 25 devices
- List page=1 limit=10, page=2 limit=10, page=3 limit=10
- Assertion: Total items = 25, no duplicates across pages

## Edge Cases

**TC_DEVICE_EDGE_001: Whitespace in name**
- Input: name = "  Device Name  "
- Expected: Trimmed to "Device Name"
- Assertion: device.name == "Device Name"

**TC_DEVICE_EDGE_002: Case-insensitive filter**
- Input: name_filter = "TEMPERATURE"
- Create device with name "temperature sensor"
- Expected: Device included in results
- Assertion: Device found

**TC_DEVICE_EDGE_003: Special characters in name**
- Input: name = "Device-123_A1"
- Expected: Persisted correctly
- Assertion: device.name == "Device-123_A1"

**TC_DEVICE_EDGE_004: Maximum length values**
- Input: name = "x"*128, model = "y"*128, location = "z"*256
- Expected: All persisted correctly
- Assertion: All fields match input

**TC_DEVICE_EDGE_005: Concurrent creation**
- Two requests create devices simultaneously
- Expected: Both succeed with unique IDs
- Assertion: device1.id != device2.id

## Performance Test Cases

**TC_DEVICE_PERF_001: List 1000 devices**
- Create 1000 devices
- List with limit=100
- Expected: Response < 1s
- Assertion: Timing assertion

**TC_DEVICE_PERF_002: Index effectiveness for name filter**
- Create 10000 devices
- Filter by name
- Expected: Uses index, response < 100ms
- Assertion: Timing assertion

## Error Handling Test Cases

**TC_DEVICE_ERROR_001: Database connection fails**
- Mock database error
- Input: Create device
- Expected: DatabaseError raised
- Assertion: HTTP 500 returned

**TC_DEVICE_ERROR_002: UUID format validation**
- Input: device_id = "invalid-uuid"
- Expected: Pydantic validation error
- Assertion: HTTP 422 returned

**TC_DEVICE_ERROR_003: Missing required field**
- Input: Create request without name
- Expected: Pydantic validation error
- Assertion: HTTP 422 returned

## Security Test Cases

**TC_DEVICE_SEC_001: SQL injection in name filter**
- Input: name_filter = "'; DROP TABLE devices; --"
- Expected: Treated as literal string
- Assertion: No SQL injection, query succeeds

**TC_DEVICE_SEC_002: UUID tampering**
- Input: device_id = "admin-device-id"
- Expected: UUID validation fails
- Assertion: HTTP 422 returned

**TC_DEVICE_SEC_003: created_by immutability**
- Create device with created_by=A
- Try to update created_by to B
- Expected: created_by remains A
- Assertion: device.created_by == original_value
