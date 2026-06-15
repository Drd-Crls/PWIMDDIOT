from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from fastapi import status
from app.services.token_service import TokenService
from app.interfaces.services import TokenServiceInterface
from app.repositories.user_repository import UserRepository
from app.settings.database import SessionLocal
from app.schemas.user import UserResponse


EXEMPT_PATHS = {"/openapi.json", "/docs", "/redoc", "/favicon.ico"}
EXEMPT_PREFIXES = ("/auth",)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in EXEMPT_PATHS or path.startswith(EXEMPT_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("authorization")

        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = parts[1]
        token_service: TokenServiceInterface = TokenService()
        payload = token_service.decode_token(token)
        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token payload"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        db = SessionLocal()
        try:
            user_repo = UserRepository(db)
            user = user_repo.get_by_id(user_id)
            if user is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "User not found"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

            try:
                request.state.user = UserResponse.model_validate(user)
            except Exception:
                request.state.user = None
        finally:
            db.close()

        return await call_next(request)
