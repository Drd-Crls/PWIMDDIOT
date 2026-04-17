from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.enums.role import Role


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: Role
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
