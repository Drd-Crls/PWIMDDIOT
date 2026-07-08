from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Tuple
from app.repositories.ingest_repository import IngestRepository
from app.repositories.sensor_repository import SensorRepository
from app.services.ingest_service import IngestService
from app.interfaces.services import IngestServiceInterface
from app.schemas.ingest import IngestCreateRequest, IngestUpdateRequest
from app.interfaces.controllers import IngestControllerInterface
from app.models.ingest import Ingest


class IngestController(IngestControllerInterface):

    def __init__(self, db: Session):
        self.db = db
        self.ingest_repository = IngestRepository(db)
        self.sensor_repository = SensorRepository(db)
        self.ingest_service: IngestServiceInterface = IngestService(
            self.ingest_repository,
            self.sensor_repository,
        )

    def create(self, req: IngestCreateRequest) -> Ingest:
        return self.ingest_service.create_ingest(
            metadata=req.metadata,
            sensor_id=req.sensor_id,
        )

    def list(
        self,
        page: int = 1,
        limit: int = 10,
        sensor_id: Optional[UUID] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Ingest], int]:
        return self.ingest_service.list_ingests(
            page=page,
            limit=limit,
            sensor_id=sensor_id,
            created_from=created_from,
            created_to=created_to,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get(self, ingest_id: UUID) -> Ingest:
        return self.ingest_service.get_ingest(ingest_id)

    def update(self, ingest_id: UUID, req: IngestUpdateRequest) -> Ingest:
        return self.ingest_service.update_ingest(
            ingest_id=ingest_id,
            metadata=req.metadata,
            sensor_id=req.sensor_id,
        )

    def delete(self, ingest_id: UUID) -> None:
        return self.ingest_service.delete_ingest(ingest_id)
