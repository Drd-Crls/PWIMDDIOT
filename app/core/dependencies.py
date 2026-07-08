from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.settings.database import get_db
from app.services.token_service import TokenService
from app.interfaces.services import TokenServiceInterface
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse
from app.schemas.api_key import ApiKeyContext
from app.core.permissions import PermissionValidator
from app.core.exceptions import UnauthorizedError

security = HTTPBearer()


async def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    token = credentials.credentials
    token_service: TokenServiceInterface = TokenService()
    payload = token_service.decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserResponse.model_validate(user)


def get_api_key_context(request: Request) -> ApiKeyContext:
    context = getattr(request.state, "api_key_context", None)
    if context is None:
        raise UnauthorizedError("API Key authentication required")
    return context


def require_api_key_permission(resource: str, action: str):
    def dependency(request: Request) -> ApiKeyContext:
        context = get_api_key_context(request)
        PermissionValidator.ensure_permission(context.permissions, resource, action)
        return context

    return dependency
