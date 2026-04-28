# CONSTITUTION.md - Immutable Project Principles

## Stack Commitment
- **Framework**: FastAPI (async-first, modern Python web framework)
- **ORM**: SQLAlchemy 2.0+ (async support)
- **Database**: PostgreSQL 15+ (strong typing, JSON support)
- **Auth**: JWT (via python-jose) with bcrypt password hashing
- **Schema Validation**: Pydantic v2
- **Dependency Injection**: dependency-injector library
- **Task Management**: Alembic migrations (for schema versioning)

## Architecture Pattern: Clean Architecture
- **Route Layer** (`routes/`) → HTTP entry points only
- **Controller Layer** (`controllers/`) → request orchestration, no business logic
- **Service Layer** (`services/`) → business logic, orchestration
- **Repository Layer** (`repositories/`) → data access abstraction (interface-based)
- **Model Layer** (`models/`) → SQLAlchemy ORM entities (database truth)
- **Schema Layer** (`schemas/`) → Pydantic DTOs (request/response contracts)

## Code Conventions (MUST NOT VIOLATE)

### Dependency Inversion
- **NEVER** import directly from Models in Controllers or Routes
- **ONLY** use Repositories via `UserRepositoryInterface` abstract class (not concrete implementations)
- Controllers and Routes receive dependencies via FastAPI `Depends()` and container injection

### Authentication & Authorization
- Use HTTPBearer security scheme, extract token via `dependencies.get_current_user()`
- Tokens include `sub` (user_id) and `role` claims
- Password validation happens in Service layer only (never in Controller)

### Error Handling
- Raise custom `AppException` subclasses: `ValidationError`, `ConflictError`, `NotFoundError`, `UnauthorizedError`, `DatabaseError`
- Repository layer catches `IntegrityError` and maps to appropriate exception
- Exception handlers in `core/exception_handlers.py` convert to HTTP responses

### Data Types
- Use `UUID` (uuid4) for all entity IDs (not integer auto-increment)
- Use `Enum` for fixed value sets (e.g., `Role.ADMIN`, `Role.USER`)
- All timestamps (created_at, updated_at) are `datetime` with UTC

### Database State
- Repositories are the ONLY layer that writes to database
- Services calculate/transform, Repositories persist
- Always call `db.commit()` and `db.refresh(entity)` after write operations

### Container & Injection
- All Controllers must be instantiated through `app.core.container.Container`
- Services are created as Factory providers, not Singleton
- Database session is Callable provider (new per request)

## What NEVER Gets Done
1. ❌ Direct database queries in Controllers or Routes
2. ❌ Business logic in HTTP route functions
3. ❌ Plaintext passwords (always hash with bcrypt)
4. ❌ Monolithic services (split when >300 LOC)
5. ❌ Catching broad `Exception` (always be specific)
6. ❌ Hardcoded config values (use `.env` via Pydantic Settings)
7. ❌ Modifying Models without Alembic migration
8. ❌ Returning raw SQLAlchemy models in API responses (use Schemas)
9. ❌ Database transactions managed manually (rely on SQLAlchemy context manager)
10. ❌ Async code in business logic without justified design doc
