from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class SensorResponse(BaseModel):
    id: UUID
    name: str
    type: str
    unit: Optional[str] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    device_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SensorCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    type: str = Field(..., min_length=1, max_length=128)
    unit: Optional[str] = Field(None, max_length=64)
    min_value: Optional[Decimal] = Field(None)
    max_value: Optional[Decimal] = Field(None)
    device_id: UUID = Field(...)

    @model_validator(mode="after")
    def validate_value_range(self) -> "SensorCreateRequest":
        if self.min_value is not None and self.max_value is not None:
            if self.max_value < self.min_value:
                raise ValueError("'max_value' must be greater than or equal to 'min_value'")
        return self


class SensorUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    type: Optional[str] = Field(None, min_length=1, max_length=128)
    unit: Optional[str] = Field(None, max_length=64)
    min_value: Optional[Decimal] = Field(None)
    max_value: Optional[Decimal] = Field(None)
    device_id: Optional[UUID] = Field(None)


class SensorListResponse(BaseModel):
    items: List[SensorResponse]
    total: int
    page: int
    limit: int
