from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.sensor import Sensor
from app.core.exceptions import DatabaseError, ConflictError
from app.interfaces.repositories import SensorRepositoryInterface


class SensorRepository(SensorRepositoryInterface):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sensor_id: UUID) -> Optional[Sensor]:
        return self.db.query(Sensor).filter(Sensor.id == sensor_id).first()

    def list(
        self,
        offset: int,
        limit: int,
        name_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        unit_filter: Optional[str] = None,
        device_id_filter: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Sensor], int]:
        query = self.db.query(Sensor)

        if name_filter:
            query = query.filter(Sensor.name.ilike(f"%{name_filter}%"))
        if type_filter:
            query = query.filter(Sensor.type.ilike(f"%{type_filter}%"))
        if unit_filter:
            query = query.filter(Sensor.unit.ilike(f"%{unit_filter}%"))
        if device_id_filter:
            query = query.filter(Sensor.device_id == device_id_filter)

        total = query.count()

        sort_column = getattr(Sensor, sort_by, Sensor.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        items = query.offset(offset).limit(limit).all()

        return items, total

    def create(self, sensor: Sensor) -> Sensor:
        try:
            self.db.add(sensor)
            self.db.commit()
            self.db.refresh(sensor)
            return sensor
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            if "device_id" in error_msg and "fk" in error_msg.lower():
                raise ConflictError("Referenced device does not exist")
            raise DatabaseError(f"Database integrity error: {error_msg}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))

    def update(self, sensor: Sensor) -> Sensor:
        try:
            self.db.add(sensor)
            self.db.commit()
            self.db.refresh(sensor)
            return sensor
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            if "device_id" in error_msg and "fk" in error_msg.lower():
                raise ConflictError("Referenced device does not exist")
            raise DatabaseError(f"Database integrity error: {error_msg}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))

    def delete(self, sensor: Sensor) -> None:
        try:
            self.db.delete(sensor)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError("Cannot delete sensor: it is referenced by other entities")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))
