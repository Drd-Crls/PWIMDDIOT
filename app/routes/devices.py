from fastapi import APIRouter, Depends, status
from typing import Optional
from uuid import UUID
from app.controllers.device_controller import DeviceController
from app.schemas.device import (
    DeviceResponse,
    DeviceCreateRequest,
    DeviceUpdateRequest,
    DeviceListResponse,
)
from app.core.container import get_device_controller

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Device",
    description="Create a new IoT device in the system"
)
def create_device(
    create_request: DeviceCreateRequest,
    controller: DeviceController = Depends(get_device_controller),
):
    """
    Create a new device.
    
    Required fields:
    - name: Device name (1-128 chars)
    - model: Device model (1-128 chars)
    - status: Device status (ACTIVE, INACTIVE, MAINTENANCE, OFFLINE)
    - context_id: UUID of context this device belongs to
    - created_by: UUID of user creating this device
    
    Optional fields:
    - location: Device location (max 256 chars)
    
    Returns 201 with created device or 400/409 on validation/conflict error.
    """
    return controller.create(create_request)


@router.get(
    "",
    response_model=DeviceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Devices",
    description="List all devices with pagination, filtering, and sorting"
)
def list_devices(
    page: int = 1,
    limit: int = 10,
    name: Optional[str] = None,
    model: Optional[str] = None,
    status: Optional[str] = None,
    context_id: Optional[UUID] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    controller: DeviceController = Depends(get_device_controller),
):
    """
    List devices with advanced filtering and pagination.
    
    Query Parameters:
    - page: Page number (default: 1, min: 1)
    - limit: Items per page (default: 10, min: 1, max: 100)
    - name: Filter by device name (case-insensitive substring)
    - model: Filter by device model (case-insensitive substring)
    - status: Filter by device status (ACTIVE, INACTIVE, MAINTENANCE, OFFLINE)
    - context_id: Filter by context UUID
    - sort_by: Sort column (name, model, status, created_at, updated_at)
    - sort_order: Sort direction (asc, desc)
    
    Returns paginated list with total count.
    """
    items, total = controller.list(
        page=page,
        limit=limit,
        name=name,
        model=model,
        status=status,
        context_id=context_id,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Device",
    description="Get a specific device by ID"
)
def get_device(
    device_id: UUID,
    controller: DeviceController = Depends(get_device_controller),
):
    """
    Get device by UUID.
    
    Returns 200 with device or 404 if not found.
    """
    return controller.get(device_id)


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Device",
    description="Update device fields"
)
def update_device(
    device_id: UUID,
    update_request: DeviceUpdateRequest,
    controller: DeviceController = Depends(get_device_controller),
):
    """
    Update a device.
    
    All fields optional (PATCH-like behavior). Only provided fields are updated.
    - name: New device name (optional)
    - model: New device model (optional)
    - status: New device status (optional)
    - location: New device location (optional)
    
    Returns 200 with updated device or 404 if not found.
    """
    return controller.update(device_id, update_request)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Device",
    description="Delete a device from the system"
)
def delete_device(
    device_id: UUID,
    controller: DeviceController = Depends(get_device_controller),
):
    """
    Delete a device.
    
    Returns 200 on success or 404 if device not found.
    Returns 409 if device is still referenced by other entities.
    """
    controller.delete(device_id)
    return {"detail": "Device deleted"}
