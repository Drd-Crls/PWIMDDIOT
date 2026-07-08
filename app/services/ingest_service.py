from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.ingest import Ingest
from app.core.exceptions import ValidationError, NotFoundError, ConflictError
from app.interfaces.services import IngestServiceInterface
from app.interfaces.repositories import IngestRepositoryInterface, SensorRepositoryInterface

VALID_SORT_COLUMNS = {"sensor_id", "created_at", "updated_at"}


class IngestService(IngestServiceInterface):

    def __init__(
        self,
        ingest_repository: IngestRepositoryInterface,
        sensor_repository: SensorRepositoryInterface,
    ):
        self.ingest_repository = ingest_repository
        self.sensor_repository = sensor_repository

    def _ensure_sensor_exists(self, sensor_id: UUID) -> None:
        sensor = self.sensor_repository.get_by_id(sensor_id)
        if not sensor:
            raise ConflictError("Referenced sensor does not exist")

    def _validate_metadata(self, metadata: Optional[Dict[str, Any]]) -> None:
        if metadata is None:
            raise ValidationError("'metadata' is required")
        if not isinstance(metadata, dict):
            raise ValidationError("'metadata' must be a valid JSON object")
        if len(metadata) == 0:
            raise ValidationError("'metadata' cannot be empty")

    def create_ingest(self, metadata: Dict[str, Any], sensor_id: UUID) -> Ingest:
        self._validate_metadata(metadata)
        self._ensure_sensor_exists(sensor_id)

        new_ingest = Ingest(
            ingest_metadata=metadata,
            sensor_id=sensor_id,
        )

        return self.ingest_repository.create(new_ingest)

    def list_ingests(
        self,
        page: int = 1,
        limit: int = 10,
        sensor_id: Optional[UUID] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[list, int]:
        if page < 1:
            raise ValidationError("'page' must be >= 1")
        if limit < 1 or limit > 100:
            raise ValidationError("'limit' must be between 1 and 100")
        if sort_by not in VALID_SORT_COLUMNS:
            raise ValidationError(f"'sort_by' must be one of {VALID_SORT_COLUMNS}")
        if created_from is not None and created_to is not None and created_to < created_from:
            raise ValidationError("'created_to' must be greater than or equal to 'created_from'")

        offset = (page - 1) * limit
        items, total = self.ingest_repository.list(
            offset=offset,
            limit=limit,
            sensor_id_filter=sensor_id,
            created_from=created_from,
            created_to=created_to,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return items, total

    def get_ingest(self, ingest_id: UUID) -> Ingest:
        ingest = self.ingest_repository.get_by_id(ingest_id)
        if not ingest:
            raise NotFoundError("Ingest not found")
        return ingest

    def update_ingest(
        self,
        ingest_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        sensor_id: Optional[UUID] = None,
    ) -> Ingest:
        ingest = self.ingest_repository.get_by_id(ingest_id)
        if not ingest:
            raise NotFoundError("Ingest not found")

        if metadata is not None:
            self._validate_metadata(metadata)
            ingest.ingest_metadata = metadata

        if sensor_id is not None:
            self._ensure_sensor_exists(sensor_id)
            ingest.sensor_id = sensor_id

        return self.ingest_repository.update(ingest)

    def delete_ingest(self, ingest_id: UUID) -> None:
        ingest = self.ingest_repository.get_by_id(ingest_id)
        if not ingest:
            raise NotFoundError("Ingest not found")
        self.ingest_repository.delete(ingest)
