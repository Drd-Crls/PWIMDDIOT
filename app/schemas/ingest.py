from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class IngestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    metadata: Dict[str, Any] = Field(
        validation_alias="ingest_metadata",
        serialization_alias="metadata",
    )
    sensor_id: UUID
    created_at: datetime
    updated_at: datetime


class IngestCreateRequest(BaseModel):
    metadata: Dict[str, Any] = Field(...)
    sensor_id: UUID = Field(...)

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("'metadata' must be a valid JSON object")
        if len(value) == 0:
            raise ValueError("'metadata' cannot be empty")
        return value


class IngestUpdateRequest(BaseModel):
    metadata: Optional[Dict[str, Any]] = Field(None)
    sensor_id: Optional[UUID] = Field(None)

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if value is None:
            return value
        if not isinstance(value, dict):
            raise ValueError("'metadata' must be a valid JSON object")
        if len(value) == 0:
            raise ValueError("'metadata' cannot be empty")
        return value


class IngestListResponse(BaseModel):
    items: List[IngestResponse]
    total: int
    page: int
    limit: int
