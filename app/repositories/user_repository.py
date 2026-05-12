from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.interfaces.repositories import UserRepositoryInterface
from app.core.exceptions import ConflictError, DatabaseError


class UserRepository(UserRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user: User) -> User:
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e).lower() or "ix_users_email" in str(e):
                raise ConflictError(f"Email '{user.email}' already registered.")
            elif "duplicate key" in str(e).lower():
                raise ConflictError("This resource already exists.")
            else:
                raise DatabaseError(f"Database constraint violation: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Database error: {str(e)}")
