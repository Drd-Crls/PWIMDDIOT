# conventions.md - Code Patterns & Style

## Folder Structure Conventions

```
app/
├── models/              # SQLAlchemy ORM entities (database schema)
├── schemas/             # Pydantic request/response DTOs
├── repositories/        # Data access layer
│   ├── base_repository.py   # Abstract interfaces
│   └── {entity}_repository.py
├── services/            # Business logic
│   ├── {entity}_service.py
│   └── token_service.py     # Crypto/JWT operations
├── controllers/         # HTTP orchestration
│   └── {entity}_controller.py
├── routes/              # FastAPI routers
│   └── {entity}.py
├── enums/               # Fixed value sets
│   └── role.py
├── core/                # Core infrastructure
│   ├── config.py            # Settings from .env
│   ├── container.py         # Dependency injection container
│   ├── dependencies.py      # FastAPI dependency providers
│   ├── security.py          # Cryptography utilities
│   ├── exceptions.py        # Custom exception classes
│   └── exception_handlers.py # Exception → HTTP response mapping
├── database.py          # SQLAlchemy setup (engine, sessionmaker, Base)
└── main.py              # FastAPI app instantiation
```

## Naming Conventions

### Files & Directories
- **Models**: singular lowercase + `_repository.py` → `user_repository.py`
- **Controllers**: `{entity}_controller.py` → `auth_controller.py`
- **Services**: `{entity}_service.py` → `auth_service.py`
- **Routes**: `{entity}.py` (plural on router prefix) → `users.py` with `prefix="/users"`
- **Enums**: `{name}.py` → `role.py` with values `Role.ADMIN`, `Role.USER`
- **Schemas**: `{entity}.py` → `user.py` with `UserCreateRequest`, `UserResponse`

### Classes
- Controllers: `{Entity}Controller` (PascalCase) → `AuthController`
- Services: `{Entity}Service` → `UserService`
- Repositories: `{Entity}Repository` + `{Entity}RepositoryInterface` → `UserRepository(UserRepositoryInterface)`
- Exceptions: `{State}Error` → `ConflictError`, `DatabaseError`, `ValidationError`
- Pydantic Models: `{Entity}{Purpose}` → `UserCreateRequest`, `TokenResponse`, `UserResponse`
- SQLAlchemy Models: `{Entity}` (singular) → `User` (table: `users`)

### Methods
- Query methods: `get_by_{field}()` → `get_by_email()`, `get_by_id()`
- Creators: `create()` → repository pattern
- Services: action verbs → `login()`, `register()`, `verify_token()`

### Variables
- Database sessions: `db` (lowercase)
- Request DTOs: `{entity}_request` → `user_request`, `login_request`
- Exceptions: caught as `as e`
- UUID variables: `{entity}_id` or just `id` → `user_id`, but local `id` in repo queries

## Database & ORM Patterns

### Model Definition
```python
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from app.enums.role import Role
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.USER)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Rules**:
- Always use UUID for primary keys (not auto-increment integers)
- Always include `created_at` and `updated_at` timestamps
- Use `Enum` columns for fixed-set fields
- Index frequently-queried fields (email, user_id, etc.)

### Repository Interface Pattern
```python
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from app.models.user import User

class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def create(self, user: User) -> User:
        pass
```

**Rules**:
- Define interfaces in `base_repository.py`
- Return type hints (Optional for queries that might fail)
- Services receive interface type: `def __init__(self, user_repository: UserRepositoryInterface)`

### Repository Implementation
```python
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import ConflictError, DatabaseError

class UserRepository(UserRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e).lower():
                raise ConflictError(f"Email already registered")
            raise DatabaseError(str(e))
```

**Rules**:
- Always `db.rollback()` on exception
- Catch `IntegrityError` and map to appropriate custom exception
- Call `db.refresh()` after inserts/updates to get generated columns

## Exception Pattern

### Exception Hierarchy
```python
class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

class ValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class ConflictError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)

class NotFoundError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)
```

**Rules**:
- Public methods (service/repository) raise `AppException` subclasses
- Never catch and swallow exceptions silently
- Include context in error message (e.g., `"Email '{email}' already registered"`)

## Pydantic Schema Pattern

### Response Schema
```python
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from app.enums.role import Role

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: Role
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 - serialize from SQLAlchemy
```

## Service Pattern

```python
class AuthService:
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
        self.token_service = TokenService()  # Create utility services here
    
    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repository.get_by_email(email)
        
        if user is None or not verify_password(password, user.password):
            raise UnauthorizedError("Invalid email or password")
        
        token = self.token_service.create_access_token({"sub": str(user.id)})
        return TokenResponse(access_token=token)
```

**Rules**:
- Public methods return DTOs or models (not raw dicts)
- Raise custom exceptions for invalid states
- Receive repositories via constructor (DI)
- Never couple to HTTP layer (no HTTPException)

## Controller Pattern

```python
class AuthController:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.auth_service = AuthService(self.user_repository)
    
    def login(self, login_request: LoginRequest) -> TokenResponse:
        return self.auth_service.login(
            login_request.email,
            login_request.password
        )
```

**Rules**:
- Minimal orchestration (mostly delegation to service)
- Constructor receives Session (not fully-bound services)
- Returns service result directly (already DTO-shaped)

## Router Pattern

```python
@router.post("/login", response_model=TokenResponse, status_code=200)
async def login(
    login_request: LoginRequest,
    auth_controller: AuthController = Depends(get_auth_controller),
):
    return auth_controller.login(login_request)
```

**Rules**:
- Request/response types declared as Pydantic models
- Dependencies injected via `Depends()`
- Prefix routes by entity (`/auth`, `/users`)
- No business logic - just delegation

## Enum Pattern

```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
```

**Rules**:
- Inherit from both `str` and `Enum` for JSON serialization
- All-uppercase values with underscores if compound names
- Used in SQLAlchemy columns via `Column(Enum(Role))`

## Authentication & JWT

- **Token claims**: `{"sub": str(user_id), "role": user.role.value}`
- **Extraction**: `dependencies.get_current_user()` handles bearer token parsing
- **Return type**: `UserResponse` with parsed user data from token
- **Error handling**: Invalid/expired tokens raise `UnauthorizedError`

