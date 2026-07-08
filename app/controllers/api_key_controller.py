from typing import List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.api_key_repository import ApiKeyRepository
from app.repositories.user_repository import UserRepository
from app.services.api_key_generator import ApiKeyGenerator
from app.services.api_key_service import ApiKeyService
from app.interfaces.services import ApiKeyServiceInterface
from app.interfaces.controllers import ApiKeyControllerInterface
from app.schemas.api_key import ApiKeyCreateRequest
from app.models.api_key import ApiKey


class ApiKeyController(ApiKeyControllerInterface):

    def __init__(self, db: Session):
        self.db = db
        self.api_key_repository = ApiKeyRepository(db)
        self.user_repository = UserRepository(db)
        self.api_key_generator = ApiKeyGenerator()
        self.api_key_service: ApiKeyServiceInterface = ApiKeyService(
            self.api_key_repository,
            self.api_key_generator,
            self.user_repository,
        )

    def create(self, user_id: UUID, req: ApiKeyCreateRequest) -> Tuple[ApiKey, str]:
        return self.api_key_service.create_api_key(
            user_id=user_id,
            permissions=req.permissions,
        )

    def list(self, user_id: UUID) -> List[ApiKey]:
        return self.api_key_service.list_api_keys(user_id)

    def revoke(self, api_key_id: UUID, user_id: UUID) -> ApiKey:
        return self.api_key_service.revoke_api_key(api_key_id, user_id)

    def rotate(self, api_key_id: UUID, user_id: UUID) -> Tuple[ApiKey, str]:
        return self.api_key_service.rotate_api_key(api_key_id, user_id)
