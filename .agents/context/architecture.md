# architecture.md - System Organization

## High-Level Data Flow

```
HTTP Request
    ↓
routes/{feature}.py (APIRouter - entry point, no logic)
    ↓ (FastAPI Depends)
controllers/{feature}_controller.py (orchestration, delegates to service)
    ↓ (constructor injection)
services/{feature}_service.py (business logic + token/crypto operations)
    ↓ (constructor injection)
repositories/{entity}_repository.py (data access, implements Interface)
    ↓
models/{entity}.py (SQLAlchemy ORM, database schema truth)
    ↓
PostgreSQL Database

Outbound:
    responses use schemas/{entity}.py (Pydantic DTOs)
    ✓ Serialized to JSON
    ✓ Validates output shape
```

## Layer Responsibilities

### Route Layer (`routes/`)
- Define FastAPI routers with path operations
- Declare dependencies via `Depends()` 
- Accept Pydantic request schemas
- Return Pydantic response schemas
- **NEVER** contains logic

Example pattern:
```python
@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    return controller.login(req)
```

### Controller Layer (`controllers/`)
- Receives HTTP request DTOs (already validated by FastAPI/Pydantic)
- Instantiates or receives Service dependencies via constructor
- Calls service methods, returns response DTOs
- Catches and re-raises meaningful errors (let custom exceptions bubble)
- **NO** direct database access

Example pattern:
```python
class AuthController:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.auth_service = AuthService(self.user_repository)
    
    def login(self, login_request: LoginRequest) -> TokenResponse:
        return self.auth_service.login(login_request.email, login_request.password)
```

### Service Layer (`services/`)
- Encapsulates business logic
- Orchestrates multiple repositories if needed
- Handles token generation, password verification, calculations
- Raises custom exceptions for invalid operations
- **MUST NOT** have HTTP knowledge (no HTTPException directly - raise AppException)
- Receives repositories via constructor (dependency inversion)

Example pattern:
```python
class AuthService:
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
        self.token_service = TokenService()
    
    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repository.get_by_email(email)
        if not verify_password(password, user.password):
            raise UnauthorizedError("Invalid credentials")
        token = self.token_service.create_access_token({"sub": str(user.id)})
        return TokenResponse(access_token=token)
```

### Repository Layer (`repositories/`)
- Queries and persists data
- Implements abstract interface (e.g., `UserRepositoryInterface`)
- Wraps database errors into custom exceptions
- Only layer that calls `db.add()`, `db.commit()`, `db.refresh()`
- Used by Services, **never** by Controllers directly

Example pattern:
```python
class UserRepository(UserRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, user: User) -> User:
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise ConflictError(f"Email already registered")
```

### Model Layer (`models/`)
- SQLAlchemy declarative models
- Defines database schema and types
- **ONLY** touched when schema changes (via Alembic migrations)

### Schema Layer (`schemas/`)
- Pydantic models for request/response validation
- Separates API contract from database schema
- Enables response filtering (e.g., exclude password field)
- Field validation happens automatically

Example pattern:
```python
class UserResponse(BaseModel):
    id: UUID
    email: str
    role: Role
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 compatible with SQLAlchemy

class UserCreateRequest(BaseModel):
    email: str
    password: str
    role: Role
```

## Core Utilities

### Dependency Injection (`core/container.py`)
- Global `Container` class manages all service instances
- Providers defined as Factory or Callable
- Factory = new instance per request
- Callable = call function each time (for SessionLocal)

### Dependencies (`core/dependencies.py`)
- `get_current_user()` - extracts & validates JWT token
- `get_db()` - provides SQLAlchemy session

### Security (`core/security.py`)
- `hash_password()` - bcrypt hashing
- `verify_password()` - constant-time comparison
- Token operations in separate `TokenService`

### Config (`core/config.py`)
- Reads `.env` via Pydantic Settings
- Single source of truth for environment config

### Exception Handling (`core/exception_handlers.py`)
- Maps custom `AppException` to HTTP responses
- Registered in `main.py`

## Database Connection

```
main.py creates engine + sessionmaker
  ↓
get_db() provides Session to controllers via FastAPI Depends
  ↓
Controllers pass Session to Repository
  ↓
Repository runs queries
  ↓
Session closed in finally block (guaranteed)
```

## Current Features

| Feature | Route | Controller | Service | Repository |
|---------|-------|------------|---------|------------|
| **Login** | POST `/auth/login` | AuthController.login() | AuthService.login() | UserRepository.get_by_email() |
| **Get Current User** | GET `/auth/me` | (dependency handler) | - | UserRepository.get_by_id() |
| **Register User** | POST `/users` | UserController.create_user() | UserService.create_user() | UserRepository.create() |

