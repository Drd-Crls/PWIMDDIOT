from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.api_key import ApiKey
from app.core.exceptions import DatabaseError, ConflictError
from app.interfaces.repositories import ApiKeyRepositoryInterface


class ApiKeyRepository(ApiKeyRepositoryInterface):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, api_key_id: UUID) -> Optional[ApiKey]:
        return self.db.query(ApiKey).filter(ApiKey.id == api_key_id).first()

    def get_by_hash(self, key_hash: str) -> Optional[ApiKey]:
        return self.db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()

    def list_by_user(self, user_id: UUID) -> List[ApiKey]:
        return (
            self.db.query(ApiKey)
            .filter(ApiKey.user_id == user_id)
            .order_by(ApiKey.created_at.desc())
            .all()
        )

    def create(self, api_key: ApiKey) -> ApiKey:
        try:
            self.db.add(api_key)
            self.db.commit()
            self.db.refresh(api_key)
            return api_key
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            if "key_hash" in error_msg:
                raise ConflictError("API Key hash collision, please retry")
            if "user_id" in error_msg and "fk" in error_msg.lower():
                raise ConflictError("Referenced user does not exist")
            raise DatabaseError(f"Database integrity error: {error_msg}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))

    def update(self, api_key: ApiKey) -> ApiKey:
        try:
            self.db.add(api_key)
            self.db.commit()
            self.db.refresh(api_key)
            return api_key
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseError(f"Database integrity error: {str(e.orig)}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))
