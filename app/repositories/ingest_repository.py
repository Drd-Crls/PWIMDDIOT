from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.ingest import Ingest
from app.core.exceptions import DatabaseError, ConflictError
from app.interfaces.repositories import IngestRepositoryInterface


class IngestRepository(IngestRepositoryInterface):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ingest_id: UUID) -> Optional[Ingest]:
        return self.db.query(Ingest).filter(Ingest.id == ingest_id).first()

    def list(
        self,
        offset: int,
        limit: int,
        sensor_id_filter: Optional[UUID] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Ingest], int]:
        query = self.db.query(Ingest)

        if sensor_id_filter:
            query = query.filter(Ingest.sensor_id == sensor_id_filter)
        if created_from:
            query = query.filter(Ingest.created_at >= created_from)
        if created_to:
            query = query.filter(Ingest.created_at <= created_to)

        total = query.count()

        sort_column = getattr(Ingest, sort_by, Ingest.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        items = query.offset(offset).limit(limit).all()

        return items, total

    def create(self, ingest: Ingest) -> Ingest:
        try:
            self.db.add(ingest)
            self.db.commit()
            self.db.refresh(ingest)
            return ingest
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            if "sensor_id" in error_msg and "fk" in error_msg.lower():
                raise ConflictError("Referenced sensor does not exist")
            raise DatabaseError(f"Database integrity error: {error_msg}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))

    def update(self, ingest: Ingest) -> Ingest:
        try:
            self.db.add(ingest)
            self.db.commit()
            self.db.refresh(ingest)
            return ingest
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            if "sensor_id" in error_msg and "fk" in error_msg.lower():
                raise ConflictError("Referenced sensor does not exist")
            raise DatabaseError(f"Database integrity error: {error_msg}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))

    def delete(self, ingest: Ingest) -> None:
        try:
            self.db.delete(ingest)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError("Cannot delete ingest: it is referenced by other entities")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))
