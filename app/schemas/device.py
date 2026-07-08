from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from app.enums.device_status import DeviceStatus


class DeviceResponse(BaseModel):
    """
    Device response DTO for API responses.
    
    Used in:
    - GET /devices/{id}
    - POST /devices (created resource)
    - PUT /devices/{id} (updated resource)
    """
    id: UUID
    name: str
    model: str
    location: Optional[str] = None
    status: DeviceStatus
    context_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeviceCreateRequest(BaseModel):
    """
    Device creation request DTO.
    
    Validation Rules:
    - name: required, 1-128 characters, whitespace trimmed
    - model: required, 1-128 characters, whitespace trimmed
    - location: optional, max 256 characters
    - status: required, must be valid DeviceStatus enum value
    - context_id: required, must be valid UUID referencing existing Context
    - created_by: required, must be valid UUID referencing existing User
    """
    name: str = Field(..., min_length=1, max_length=128, description="Device name")
    model: str = Field(..., min_length=1, max_length=128, description="Device model")
    location: Optional[str] = Field(None, max_length=256, description="Device location")
    status: DeviceStatus = Field(..., description="Device status")
    context_id: UUID = Field(..., description="Context UUID this device belongs to")
    created_by: UUID = Field(..., description="User UUID who created this device")


class DeviceUpdateRequest(BaseModel):
    """
    Device update request DTO.
    
    Validation Rules:
    - All fields optional (PATCH-like behavior)
    - If provided, must meet same validation as create request
    - updated_at automatically managed by repository
    """
    name: Optional[str] = Field(None, min_length=1, max_length=128, description="Device name")
    model: Optional[str] = Field(None, min_length=1, max_length=128, description="Device model")
    location: Optional[str] = Field(None, max_length=256, description="Device location")
    status: Optional[DeviceStatus] = Field(None, description="Device status")


class DeviceListResponse(BaseModel):
    """
    Paginated device list response DTO.
    
    Used in:
    - GET /devices (with pagination and filtering)
    
    Fields:
    - items: List of device responses
    - total: Total count of devices matching filter (before pagination)
    - page: Current page number (1-based)
    - limit: Items per page
    """
    items: List[DeviceResponse]
    total: int
    page: int
    limit: int
