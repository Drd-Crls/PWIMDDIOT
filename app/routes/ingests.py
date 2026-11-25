import logging
import time
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
from app.core.logging import duration_label, now_label

router = APIRouter(prefix="/ingests", tags=["ingests"])

logger = logging.getLogger(__name__)

SEPARATOR = "-" * 70


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
    started_at = time.perf_counter()
    logger.info(
        "\n%s\nCOMEÇOU: chegou um pedido para guardar uma nova leitura de sensor."
        "\n  Horário de início: %s"
        "\n  Sensor informado:  %s\n%s",
        SEPARATOR,
        now_label(),
        create_request.sensor_id,
        SEPARATOR,
    )

    try:
        created_ingest = controller.create(create_request)
    except Exception as error:
        logger.info(
            "\n%s\nTERMINOU COM ERRO: a leitura não pôde ser guardada."
            "\n  Horário de término: %s"
            "\n  Tempo até o erro:   %s"
            "\n  Motivo:             %s\n%s",
            SEPARATOR,
            now_label(),
            duration_label((time.perf_counter() - started_at) * 1000),
            error,
            SEPARATOR,
        )
        raise

    logger.info(
        "\n%s\nTERMINOU: a leitura foi guardada com sucesso."
        "\n  Horário de término: %s"
        "\n  Tempo total:        %s\n%s",
        SEPARATOR,
        now_label(),
        duration_label((time.perf_counter() - started_at) * 1000),
        SEPARATOR,
    )
    return created_ingest


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
