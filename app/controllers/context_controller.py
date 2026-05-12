from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Tuple
from app.repositories.context_repository import ContextRepository
from app.services.context_service import ContextService
from app.interfaces.services import ContextServiceInterface
from app.schemas.context import ContextCreateRequest, ContextUpdateRequest
from app.interfaces.controllers import ContextControllerInterface
from app.models.context import Context


class ContextController(ContextControllerInterface):
    def __init__(self, db: Session):
        self.db = db
        self.context_repository = ContextRepository(db)
        self.context_service: ContextServiceInterface = ContextService(self.context_repository)

    def create(self, req: ContextCreateRequest) -> Context:
        return self.context_service.create_context(name=req.name, description=req.description)

    def list(self, page: int = 1, limit: int = 10, name: Optional[str] = None) -> Tuple[List[Context], int]:
        return self.context_service.list_contexts(page=page, limit=limit, name=name)

    def get(self, context_id: UUID) -> Context:
        return self.context_service.get_context(context_id)

    def update(self, context_id: UUID, req: ContextUpdateRequest) -> Context:
        return self.context_service.update_context(context_id, name=req.name, description=req.description)

    def delete(self, context_id: UUID) -> None:
        return self.context_service.delete_context(context_id)
