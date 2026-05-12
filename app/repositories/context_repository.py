from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.context import Context
from app.core.exceptions import DatabaseError, NotFoundError
from app.interfaces.repositories import ContextRepositoryInterface


class ContextRepository(ContextRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, context_id: UUID) -> Optional[Context]:
        return self.db.query(Context).filter(Context.id == context_id).first()

    def list(self, offset: int, limit: int, name_filter: Optional[str] = None) -> Tuple[List[Context], int]:
        query = self.db.query(Context)
        if name_filter:
            query = query.filter(Context.name.ilike(f"%{name_filter}%"))
        total = query.count()
        items = query.order_by(Context.created_at.desc()).offset(offset).limit(limit).all()
        return items, total

    def create(self, context: Context) -> Context:
        try:
            self.db.add(context)
            self.db.commit()
            self.db.refresh(context)
            return context
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseError(str(e))
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))

    def update(self, context: Context) -> Context:
        try:
            self.db.add(context)
            self.db.commit()
            self.db.refresh(context)
            return context
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))

    def delete(self, context: Context) -> None:
        try:
            self.db.delete(context)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))
