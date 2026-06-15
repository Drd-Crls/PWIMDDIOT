from decimal import Decimal
from typing import Optional, Tuple
from uuid import UUID
from app.models.sensor import Sensor
from app.core.exceptions import ValidationError, NotFoundError, ConflictError
from app.interfaces.services import SensorServiceInterface
from app.interfaces.repositories import SensorRepositoryInterface, DeviceRepositoryInterface

VALID_SORT_COLUMNS = {"name", "type", "unit", "device_id", "created_at", "updated_at"}


class SensorService(SensorServiceInterface):

    def __init__(
        self,
        sensor_repository: SensorRepositoryInterface,
        device_repository: DeviceRepositoryInterface,
    ):
        self.sensor_repository = sensor_repository
        self.device_repository = device_repository

    def _ensure_device_exists(self, device_id: UUID) -> None:
        device = self.device_repository.get_by_id(device_id)
        if not device:
            raise ConflictError("Referenced device does not exist")

    def _validate_value_range(self, min_value: Optional[Decimal], max_value: Optional[Decimal]) -> None:
        if min_value is not None and max_value is not None and max_value < min_value:
            raise ValidationError("'max_value' must be greater than or equal to 'min_value'")

    def create_sensor(
        self,
        name: str,
        type: str,
        device_id: UUID,
        unit: Optional[str] = None,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
    ) -> Sensor:
        if not name or not name.strip():
            raise ValidationError("'name' is required and cannot be empty")
        if not type or not type.strip():
            raise ValidationError("'type' is required and cannot be empty")
        if len(name.strip()) > 128:
            raise ValidationError("'name' must be at most 128 characters")
        if len(type.strip()) > 128:
            raise ValidationError("'type' must be at most 128 characters")
        if unit is not None and len(unit) > 64:
            raise ValidationError("'unit' must be at most 64 characters")

        self._validate_value_range(min_value, max_value)
        self._ensure_device_exists(device_id)

        new_sensor = Sensor(
            name=name.strip(),
            type=type.strip(),
            unit=unit,
            min_value=min_value,
            max_value=max_value,
            device_id=device_id,
        )

        return self.sensor_repository.create(new_sensor)

    def list_sensors(
        self,
        page: int = 1,
        limit: int = 10,
        name: Optional[str] = None,
        type: Optional[str] = None,
        unit: Optional[str] = None,
        device_id: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[list, int]:
        if page < 1:
            raise ValidationError("'page' must be >= 1")
        if limit < 1 or limit > 100:
            raise ValidationError("'limit' must be between 1 and 100")
        if sort_by not in VALID_SORT_COLUMNS:
            raise ValidationError(f"'sort_by' must be one of {VALID_SORT_COLUMNS}")

        offset = (page - 1) * limit
        items, total = self.sensor_repository.list(
            offset=offset,
            limit=limit,
            name_filter=name,
            type_filter=type,
            unit_filter=unit,
            device_id_filter=device_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return items, total

    def get_sensor(self, sensor_id: UUID) -> Sensor:
        sensor = self.sensor_repository.get_by_id(sensor_id)
        if not sensor:
            raise NotFoundError("Sensor not found")
        return sensor

    def update_sensor(
        self,
        sensor_id: UUID,
        name: Optional[str] = None,
        type: Optional[str] = None,
        unit: Optional[str] = None,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
        device_id: Optional[UUID] = None,
    ) -> Sensor:
        sensor = self.sensor_repository.get_by_id(sensor_id)
        if not sensor:
            raise NotFoundError("Sensor not found")

        if name is not None:
            if not name.strip():
                raise ValidationError("'name' cannot be empty")
            if len(name.strip()) > 128:
                raise ValidationError("'name' must be at most 128 characters")
            sensor.name = name.strip()

        if type is not None:
            if not type.strip():
                raise ValidationError("'type' cannot be empty")
            if len(type.strip()) > 128:
                raise ValidationError("'type' must be at most 128 characters")
            sensor.type = type.strip()

        if unit is not None:
            if len(unit) > 64:
                raise ValidationError("'unit' must be at most 64 characters")
            sensor.unit = unit

        if min_value is not None:
            sensor.min_value = min_value

        if max_value is not None:
            sensor.max_value = max_value

        self._validate_value_range(sensor.min_value, sensor.max_value)

        if device_id is not None:
            self._ensure_device_exists(device_id)
            sensor.device_id = device_id

        return self.sensor_repository.update(sensor)

    def delete_sensor(self, sensor_id: UUID) -> None:
        sensor = self.sensor_repository.get_by_id(sensor_id)
        if not sensor:
            raise NotFoundError("Sensor not found")
        self.sensor_repository.delete(sensor)
