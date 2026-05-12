from __future__ import annotations
from typing import Protocol, Optional, Tuple, List
from uuid import UUID

from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreateRequest
from app.schemas.context import ContextCreateRequest, ContextUpdateRequest
from app.models.user import User
from app.models.context import Context


class AuthControllerInterface(Protocol):
    def login(self, login_request: LoginRequest) -> TokenResponse: ...


class UserControllerInterface(Protocol):
    def create_user(self, create_user_request: UserCreateRequest) -> User: ...


class ContextControllerInterface(Protocol):
    def create(self, req: ContextCreateRequest) -> Context: ...

    def list(self, page: int = 1, limit: int = 10, name: Optional[str] = None) -> Tuple[List[Context], int]: ...

    def get(self, context_id: UUID) -> Context: ...

    def update(self, context_id: UUID, req: ContextUpdateRequest) -> Context: ...

    def delete(self, context_id: UUID) -> None: ...
