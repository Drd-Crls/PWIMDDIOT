from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from uuid import UUID

from app.models.user import User
from app.models.context import Context


class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass


class ContextRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, context_id: UUID) -> Optional[Context]:
        pass

    @abstractmethod
    def list(self, offset: int, limit: int, name_filter: Optional[str] = None) -> Tuple[List[Context], int]:
        pass

    @abstractmethod
    def create(self, context: Context) -> Context:
        pass

    @abstractmethod
    def update(self, context: Context) -> Context:
        pass

    @abstractmethod
    def delete(self, context: Context) -> None:
        pass
