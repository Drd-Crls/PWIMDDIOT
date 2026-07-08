from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from fastapi import status
from app.repositories.api_key_repository import ApiKeyRepository
from app.repositories.user_repository import UserRepository
from app.services.api_key_generator import ApiKeyGenerator
from app.services.api_key_service import ApiKeyService
from app.core.exceptions import AppException
from app.settings.database import SessionLocal
from app.schemas.user import UserResponse
from app.middlewares.auth import EXEMPT_PATHS, EXEMPT_PREFIXES

API_KEY_HEADER = "x-api-key"


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in EXEMPT_PATHS or path.startswith(EXEMPT_PREFIXES):
            return await call_next(request)

        raw_key = request.headers.get(API_KEY_HEADER)
        if not raw_key:
            return await call_next(request)

        db = SessionLocal()
        try:
            service = ApiKeyService(
                ApiKeyRepository(db),
                ApiKeyGenerator(),
                UserRepository(db),
            )
            try:
                context = service.authenticate(raw_key)
            except AppException as exc:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.message, "status": exc.status_code},
                )

            user_repo = UserRepository(db)
            user = user_repo.get_by_id(context.user_id)
            if user is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "User not found"},
                )

            request.state.is_authenticated = True
            request.state.auth_type = "api_key"
            request.state.api_key_context = context
            request.state.user = UserResponse.model_validate(user)
        finally:
            db.close()

        return await call_next(request)
