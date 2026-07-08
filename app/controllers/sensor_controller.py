from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Tuple
from app.repositories.sensor_repository import SensorRepository
from app.repositories.device_repository import DeviceRepository
from app.services.sensor_service import SensorService
from app.interfaces.services import SensorServiceInterface
from app.schemas.sensor import SensorCreateRequest, SensorUpdateRequest
from app.interfaces.controllers import SensorControllerInterface
from app.models.sensor import Sensor


class SensorController(SensorControllerInterface):

    def __init__(self, db: Session):
        self.db = db
        self.sensor_repository = SensorRepository(db)
        self.device_repository = DeviceRepository(db)
        self.sensor_service: SensorServiceInterface = SensorService(
            self.sensor_repository,
            self.device_repository,
        )

    def create(self, req: SensorCreateRequest) -> Sensor:
        return self.sensor_service.create_sensor(
            name=req.name,
            type=req.type,
            device_id=req.device_id,
            unit=req.unit,
            min_value=req.min_value,
            max_value=req.max_value,
        )

    def list(
        self,
        page: int = 1,
        limit: int = 10,
        name: Optional[str] = None,
        type: Optional[str] = None,
        unit: Optional[str] = None,
        device_id: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Sensor], int]:
        return self.sensor_service.list_sensors(
            page=page,
            limit=limit,
            name=name,
            type=type,
            unit=unit,
            device_id=device_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get(self, sensor_id: UUID) -> Sensor:
        return self.sensor_service.get_sensor(sensor_id)

    def update(self, sensor_id: UUID, req: SensorUpdateRequest) -> Sensor:
        return self.sensor_service.update_sensor(
            sensor_id=sensor_id,
            name=req.name,
            type=req.type,
            unit=req.unit,
            min_value=req.min_value,
            max_value=req.max_value,
            device_id=req.device_id,
        )

    def delete(self, sensor_id: UUID) -> None:
        return self.sensor_service.delete_sensor(sensor_id)
