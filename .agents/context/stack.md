# stack.md - Technology Stack & Dependencies

## Core Stack

| Component | Technology | Version | Why |
|-----------|-----------|---------|-----|
| **Web Framework** | FastAPI | 0.104.1 | Async-first, automatic OpenAPI docs, Pydantic validation built-in, production-ready |
| **ASGI Server** | Uvicorn | 0.24.0 | High performance, async support, lightweight |
| **ORM** | SQLAlchemy | 2.0.23 | Type-safe queries, multi-database support, async ready |
| **Database** | PostgreSQL | 15 (Alpine) | Strong typing (UUID, JSON, Enum), ACID compliance, mature JSON support |
| **Migrations** | Alembic | 1.12.1 | Schema version control, reversible migrations, integrates with SQLAlchemy |
| **DB Driver** | psycopg2-binary | 2.9.9 | PostgreSQL native driver, battle-tested |

## Authentication & Security

| Component | Technology | Version | Why |
|-----------|-----------|---------|-----|
| **Auth Framework** | python-jose | 3.3.0 | JWT creation/verification, pluggable backends |
| **Crypto Backend** | cryptography | (via python-jose) | Secure token signing, HMAC support |
| **Password Hashing** | passlib + bcrypt | 1.7.4 | Industry-standard password hashing, constant-time comparison |

## Data Validation & Serialization

| Component | Technology | Version | Why |
|-----------|-----------|---------|-----|
| **Request/Response Validation** | Pydantic | 2.5.0 | Runtime type checking, automatic OpenAPI schema generation, field validators |
| **Settings Management** | pydantic-settings | 2.1.0 | `.env` file support, type-safe config loading |
| **Email Validation** | email-validator | 2.1.0 | RFC-compliant email validation for Pydantic |

## Dependency Injection

| Component | Technology | Version | Why |
|-----------|-----------|---------|-----|
| **DI Container** | dependency-injector | 4.49.0 | Type-safe container, factory providers, minimal magic |

## Environment

| Component | Stack | Version |
|-----------|-------|---------|
| **Python** | 3.11-slim | Latest stable, small Docker image |
| **Container Orchestration** | Docker Compose | 3.8 | Local dev environment, database + app together |

## Project Architecture Stack

- **Pattern**: Clean Architecture (4-layer)
- **Database Pattern**: Repository pattern with abstraction interfaces
- **Config**: Environment-based via `.env`
- **Async**: Full async/await support end-to-end (FastAPI → SQLAlchemy → ORM)
- **Type Safety**: Pydantic + Python type hints throughout

## Dependency Tree (Simplified)

```
FastAPI (HTTP framework)
  ├── Uvicorn (ASGI server)
  ├── Pydantic (validation)
  │   └── email-validator (email validation)
  ├── dependency-injector (DI container)
  └── HTTPBearer (security scheme)

SQLAlchemy (ORM)
  ├── psycopg2-binary (PostgreSQL driver)
  └── alembic (migrations)

Security
  ├── python-jose (JWT)
  │   └── cryptography (crypto backend)
  └── passlib (password hashing)
      └── bcrypt (hashing algorithm)

Config
  └── python-dotenv (env loading)
```

## Version Notes

- **Python 3.11**: EOL Dec 2027, stable security support
- **SQLAlchemy 2.0**: Major version, v1 compat mode available but not used here
- **Pydantic v2**: Complete rewrite, major API changes, now used throughout
- **PostgreSQL 15**: Latest LTS, released Oct 2022

## Container Setup

**Development**:
- `docker-compose.yml` spins up PostgreSQL 15 + FastAPI app
- Auto-reload enabled in compose for dev iteration
- Database healthcheck before app starts

**Production Ready**:
- Remove `--reload` flag
- Use environment variables for secrets (not hardcoded)
- Consider managed database instead of docker volume

## Future Considerations

- **Async context manager**: SQLAlchemy async sessions (currently synchronous)
- **Testing**: pytest + pytest-asyncio (not yet added)
- **Rate Limiting**: slowapi (not yet added)
- **Logging**: structlog or python-json-logger (not yet added)
- **Observability**: opentelemetry (not yet added)
- **Database Pooling**: tune pool_size/max_overflow in production
