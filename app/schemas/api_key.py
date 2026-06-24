from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ApiKeyCreateRequest(BaseModel):
    permissions: Dict[str, List[str]] = Field(default_factory=dict)

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, value: Dict[str, List[str]]) -> Dict[str, List[str]]:
        if not isinstance(value, dict):
            raise ValueError("'permissions' must be a valid JSON object")
        for resource, actions in value.items():
            if not isinstance(actions, list):
                raise ValueError(f"Actions for '{resource}' must be a list")
        return value


class ApiKeyCreatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    api_key: str
    permissions: Dict[str, List[str]]
    created_at: datetime


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    permissions: Dict[str, List[str]]
    created_at: datetime
    updated_at: datetime
    revoked_at: Optional[datetime] = None


class ApiKeyContext(BaseModel):
    api_key_id: UUID
    user_id: UUID
    permissions: Dict[str, List[str]]
