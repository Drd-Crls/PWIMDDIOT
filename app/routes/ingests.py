from fastapi import APIRouter, Depends, status
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.controllers.ingest_controller import IngestController
from app.schemas.ingest import (
    IngestResponse,
    IngestCreateRequest,
    IngestUpdateRequest,
    IngestListResponse,
)
from app.core.container import get_ingest_controller

router = APIRouter(prefix="/ingests", tags=["ingests"])


@router.post(
    "",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Ingest",
    description="Create a new ingest record attached to an existing sensor",
)
def create_ingest(
    create_request: IngestCreateRequest,
    controller: IngestController = Depends(get_ingest_controller),
):
    return controller.create(create_request)


@router.get(
    "",
    response_model=IngestListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Ingests",
    description="List ingest records with pagination, filtering, and sorting",
)
def list_ingests(
    page: int = 1,
    limit: int = 10,
    sensor_id: Optional[UUID] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    controller: IngestController = Depends(get_ingest_controller),
):
    items, total = controller.list(
        page=page,
        limit=limit,
        sensor_id=sensor_id,
        created_from=created_from,
        created_to=created_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get(
    "/{ingest_id}",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Ingest",
    description="Get a specific ingest record by ID",
)
def get_ingest(
    ingest_id: UUID,
    controller: IngestController = Depends(get_ingest_controller),
):
    return controller.get(ingest_id)
@router.delete(
    "/{ingest_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Ingest",
    description="Delete an ingest record from the system",
)
def delete_ingest(
    ingest_id: UUID,
    controller: IngestController = Depends(get_ingest_controller),
):
    controller.delete(ingest_id)
    return {"detail": "Ingest deleted"}
