from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime
from app.models.context import Context
from app.repositories.context_repository import ContextRepositoryInterface
from app.core.exceptions import ValidationError, NotFoundError
from app.interfaces.services import ContextServiceInterface


class ContextService(ContextServiceInterface):
    def __init__(self, context_repository: ContextRepositoryInterface):
        self.context_repository = context_repository

    def create_context(self, name: str, description: Optional[str] = None) -> Context:
        if not name or not name.strip():
            raise ValidationError("'name' is required and cannot be empty")
        if len(name.strip()) > 100:
            raise ValidationError("'name' must be at most 100 characters")

        new_context = Context(name=name.strip(), description=description)
        return self.context_repository.create(new_context)

    def list_contexts(self, page: int = 1, limit: int = 10, name: Optional[str] = None) -> Tuple[list, int]:
        if page < 1:
            raise ValidationError("'page' must be >= 1")
        if limit < 1 or limit > 100:
            raise ValidationError("'limit' must be between 1 and 100")

        offset = (page - 1) * limit
        items, total = self.context_repository.list(offset=offset, limit=limit, name_filter=name)
        return items, total

    def get_context(self, context_id: UUID) -> Context:
        ctx = self.context_repository.get_by_id(context_id)
        if not ctx:
            raise NotFoundError("Context not found")
        return ctx

    def update_context(self, context_id: UUID, name: Optional[str] = None, description: Optional[str] = None) -> Context:
        ctx = self.context_repository.get_by_id(context_id)
        if not ctx:
            raise NotFoundError("Context not found")

        if name is not None:
            if not name.strip():
                raise ValidationError("'name' cannot be empty")
            if len(name.strip()) > 100:
                raise ValidationError("'name' must be at most 100 characters")
            ctx.name = name.strip()

        if description is not None:
            ctx.description = description

        # updated_at handled by SQLAlchemy onupdate
        return self.context_repository.update(ctx)

    def delete_context(self, context_id: UUID) -> None:
        ctx = self.context_repository.get_by_id(context_id)
        if not ctx:
            raise NotFoundError("Context not found")

        # safe delete: for future relationships, repository will raise on FK constraints
        self.context_repository.delete(ctx)
