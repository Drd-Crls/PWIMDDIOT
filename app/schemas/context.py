from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, constr


class ContextResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContextCreateRequest(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=100) # type: ignore
    description: Optional[str] = None


class ContextUpdateRequest(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None # type: ignore
    description: Optional[str] = None


class ContextListResponse(BaseModel):
    items: List[ContextResponse]
    total: int
    page: int
    limit: int
