# CHANGELOG.md - Sensor Management

## Version 1.0.0 - Initial Implementation (2026-06-11)

### Added
- **Complete CRUD API for Sensor entity**
  - POST /sensors - Create new sensor
  - GET /sensors - List sensors with pagination, filtering, sorting
  - GET /sensors/{id} - Get sensor by ID
  - PUT /sensors/{id} - Update sensor
  - DELETE /sensors/{id} - Delete sensor

- **Sensor Model** (`app/models/sensor.py`)
  - UUID primary key (auto-generated)
  - name (128 char, indexed)
  - type (128 char, indexed)
  - unit (64 char, optional, indexed)
  - min_value, max_value (NUMERIC, optional)
  - device_id foreign key to devices (required, indexed)
  - created_at (indexed), updated_at timestamps (auto-managed)
  - `device` relationship with `backref="sensors"` (1:N from Device)

- **Repository Layer** (`app/repositories/sensor_repository.py`)
  - SensorRepository implements SensorRepositoryInterface
  - get_by_id / list / create / update / delete
  - FK IntegrityError on device_id mapped to ConflictError (409)

- **Service Layer** (`app/services/sensor_service.py`)
  - SensorService implements SensorServiceInterface
  - Receives SensorRepositoryInterface AND DeviceRepositoryInterface
  - Proactive device existence validation before create/update
  - Range rule (max_value >= min_value) enforced on merged state
  - Pagination and sort-column validation

- **Controller Layer** (`app/controllers/sensor_controller.py`)
  - SensorController implements SensorControllerInterface
  - Wires SensorRepository + DeviceRepository into SensorService

- **Routes Layer** (`app/routes/sensors.py`)
  - FastAPI router with all 5 CRUD endpoints
  - OpenAPI summaries/descriptions, proper status codes (201/200/400/404/409)

- **Schemas/DTOs** (`app/schemas/sensor.py`)
  - SensorResponse, SensorCreateRequest, SensorUpdateRequest, SensorListResponse
  - `model_validator` enforces max_value >= min_value at request shape
  - Decimal types for numeric fields

- **Dependency Injection** (`app/core/container.py`)
  - sensor_repository, sensor_service (with device_repository injected), sensor_controller factories
  - get_sensor_controller() provider function

- **Interface Definitions**
  - SensorRepositoryInterface in app/interfaces/repositories.py
  - SensorServiceInterface in app/interfaces/services.py
  - SensorControllerInterface in app/interfaces/controllers.py

- **App Wiring** (`app/settings/app.py`)
  - sensors_router registered on the FastAPI app

- **Database Migration**
  - `migrations/001_create_sensors_table.sql` - table + indexes (name, type, unit, device_id, created_at)

- **Code Standard**
  - All sensor source files contain zero comments/docstrings (self-explanatory naming), per the feature request's code standard. This intentionally diverges from the docstring-heavy Device feature.

### Architecture Decisions
1. **Clean Architecture**: route → controller → service → repository → model
2. **Dependency Inversion**: all dependencies referenced via interfaces
3. **DTOs**: request/response contracts separated from ORM model
4. **UUID Primary Keys**: distributed-system compatible
5. **Proactive FK Validation**: DeviceRepository injected into SensorService to verify device existence before persist (stricter than Device feature); repository IntegrityError mapping kept as safety net
6. **Dual Range Validation**: DTO validator + authoritative service check (covers partial updates)
7. **Numeric Precision**: NUMERIC columns surfaced as Decimal in DTOs
8. **Indexing**: name, type, unit, device_id, created_at for query optimization

### Database Indexes
- ix_sensors_name: name filtering
- ix_sensors_type: type filtering
- ix_sensors_unit: unit filtering
- ix_sensors_device_id: device filtering / join support
- ix_sensors_created_at: temporal sorting

### Future Enhancements
- [ ] Promote `type` to enum or lookup table
- [ ] Unique constraint on (device_id, name)
- [ ] Sensor readings / telemetry relationship (new FK referencing sensors)
- [ ] Threshold-based alerting using min/max
- [ ] Cursor-based pagination for telemetry-scale reads
- [ ] Explicit cascade strategy on Device deletion

### Breaking Changes
None - initial release

### Migration Notes
- `sensors` table requires the `devices` table to exist (FK)
- Run `migrations/001_create_sensors_table.sql`, or rely on `Base.metadata.create_all` at startup
- PostgreSQL 15+ recommended

### Dependencies
- FastAPI 0.104.1, SQLAlchemy 2.0.23, Pydantic 2.5.0, dependency-injector 4.49.0, psycopg2-binary 2.9.9

### Testing Status
- Unit / integration / E2E tests: To be implemented (see TEST_CASES.md)
- Verified at implementation time: module import via container, route registration, range-validator behavior, py_compile across all touched files

## Implementation Checklist
- [x] Sensor model created
- [x] Sensor schemas created
- [x] Sensor repository interface defined
- [x] Sensor repository implemented
- [x] Sensor service interface defined
- [x] Sensor service implemented (with device validation)
- [x] Sensor controller interface defined
- [x] Sensor controller implemented
- [x] Sensor routes created
- [x] Container updated with Sensor dependencies
- [x] app.py route registered
- [x] Database migration created (SQL)
- [x] Feature specification documented
- [x] Test cases planned
- [ ] Unit tests implemented
- [ ] Integration tests implemented

## Notes
Sensor CRUD follows established project conventions and Clean Architecture. The sensor source files are comment-free by request; the rationale and contract live here and in SPEC.md.
