from typing import Dict, List, Tuple
from datetime import datetime
from uuid import UUID
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyContext
from app.core.permissions import PermissionValidator
from app.core.exceptions import (
    NotFoundError,
    ForbiddenError,
    ConflictError,
    UnauthorizedError,
)
from app.interfaces.services import ApiKeyServiceInterface, ApiKeyGeneratorInterface
from app.interfaces.repositories import (
    ApiKeyRepositoryInterface,
    UserRepositoryInterface,
)

MAX_GENERATION_ATTEMPTS = 5


class ApiKeyService(ApiKeyServiceInterface):

    def __init__(
        self,
        api_key_repository: ApiKeyRepositoryInterface,
        api_key_generator: ApiKeyGeneratorInterface,
        user_repository: UserRepositoryInterface,
    ):
        self.api_key_repository = api_key_repository
        self.api_key_generator = api_key_generator
        self.user_repository = user_repository

    def _generate_unique_key(self) -> Tuple[str, str]:
        for _ in range(MAX_GENERATION_ATTEMPTS):
            raw_key = self.api_key_generator.generate()
            key_hash = self.api_key_generator.hash(raw_key)
            if self.api_key_repository.get_by_hash(key_hash) is None:
                return raw_key, key_hash
        raise ConflictError("Could not generate a unique API Key, please retry")

    def _get_owned_key(self, api_key_id: UUID, user_id: UUID) -> ApiKey:
        api_key = self.api_key_repository.get_by_id(api_key_id)
        if api_key is None:
            raise NotFoundError("API Key not found")
        if api_key.user_id != user_id:
            raise ForbiddenError("API Key does not belong to the authenticated user")
        return api_key

    def create_api_key(
        self, user_id: UUID, permissions: Dict[str, List[str]]
    ) -> Tuple[ApiKey, str]:
        normalized = PermissionValidator.validate(permissions)
        raw_key, key_hash = self._generate_unique_key()

        new_api_key = ApiKey(
            key_hash=key_hash,
            user_id=user_id,
            permissions=normalized,
        )
        created = self.api_key_repository.create(new_api_key)
        return created, raw_key

    def list_api_keys(self, user_id: UUID) -> List[ApiKey]:
        return self.api_key_repository.list_by_user(user_id)

    def get_api_key(self, api_key_id: UUID, user_id: UUID) -> ApiKey:
        return self._get_owned_key(api_key_id, user_id)

    def revoke_api_key(self, api_key_id: UUID, user_id: UUID) -> ApiKey:
        api_key = self._get_owned_key(api_key_id, user_id)
        if api_key.revoked_at is not None:
            raise ConflictError("API Key is already revoked")
        api_key.revoked_at = datetime.utcnow()
        return self.api_key_repository.update(api_key)

    def rotate_api_key(self, api_key_id: UUID, user_id: UUID) -> Tuple[ApiKey, str]:
        api_key = self._get_owned_key(api_key_id, user_id)
        if api_key.revoked_at is None:
            api_key.revoked_at = datetime.utcnow()
            self.api_key_repository.update(api_key)

        raw_key, key_hash = self._generate_unique_key()
        new_api_key = ApiKey(
            key_hash=key_hash,
            user_id=user_id,
            permissions=api_key.permissions,
        )
        created = self.api_key_repository.create(new_api_key)
        return created, raw_key

    def authenticate(self, raw_key: str) -> ApiKeyContext:
        if not raw_key:
            raise UnauthorizedError("Invalid API Key")

        key_hash = self.api_key_generator.hash(raw_key)
        api_key = self.api_key_repository.get_by_hash(key_hash)
        if api_key is None:
            raise UnauthorizedError("Invalid API Key")

        if not self.api_key_generator.verify(raw_key, api_key.key_hash):
            raise UnauthorizedError("Invalid API Key")

        if api_key.revoked_at is not None:
            raise UnauthorizedError("API Key has been revoked")

        user = self.user_repository.get_by_id(api_key.user_id)
        if user is None:
            raise UnauthorizedError("API Key owner no longer exists")

        return ApiKeyContext(
            api_key_id=api_key.id,
            user_id=api_key.user_id,
            permissions=api_key.permissions or {},
        )
