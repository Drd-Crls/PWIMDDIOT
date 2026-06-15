from fastapi import APIRouter, Depends, status
from typing import Optional
from uuid import UUID
from app.controllers.sensor_controller import SensorController
from app.schemas.sensor import (
    SensorResponse,
    SensorCreateRequest,
    SensorUpdateRequest,
    SensorListResponse,
)
from app.core.container import get_sensor_controller

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Sensor",
    description="Create a new sensor attached to an existing IoT device",
)
def create_sensor(
    create_request: SensorCreateRequest,
    controller: SensorController = Depends(get_sensor_controller),
):
    return controller.create(create_request)


@router.get(
    "",
    response_model=SensorListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Sensors",
    description="List sensors with pagination, filtering, and sorting",
)
def list_sensors(
    page: int = 1,
    limit: int = 10,
    name: Optional[str] = None,
    type: Optional[str] = None,
    unit: Optional[str] = None,
    device_id: Optional[UUID] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    controller: SensorController = Depends(get_sensor_controller),
):
    items, total = controller.list(
        page=page,
        limit=limit,
        name=name,
        type=type,
        unit=unit,
        device_id=device_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get(
    "/{sensor_id}",
    response_model=SensorResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Sensor",
    description="Get a specific sensor by ID",
)
def get_sensor(
    sensor_id: UUID,
    controller: SensorController = Depends(get_sensor_controller),
):
    return controller.get(sensor_id)


@router.put(
    "/{sensor_id}",
    response_model=SensorResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Sensor",
    description="Update sensor fields",
)
def update_sensor(
    sensor_id: UUID,
    update_request: SensorUpdateRequest,
    controller: SensorController = Depends(get_sensor_controller),
):
    return controller.update(sensor_id, update_request)


@router.delete(
    "/{sensor_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Sensor",
    description="Delete a sensor from the system",
)
def delete_sensor(
    sensor_id: UUID,
    controller: SensorController = Depends(get_sensor_controller),
):
    controller.delete(sensor_id)
    return {"detail": "Sensor deleted"}
