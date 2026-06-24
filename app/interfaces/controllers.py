from __future__ import annotations
from typing import Protocol, Optional, Tuple, List
from uuid import UUID
from datetime import datetime

from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreateRequest
from app.schemas.context import ContextCreateRequest, ContextUpdateRequest
from app.schemas.device import DeviceCreateRequest, DeviceUpdateRequest
from app.schemas.sensor import SensorCreateRequest, SensorUpdateRequest
from app.schemas.ingest import IngestCreateRequest, IngestUpdateRequest
from app.schemas.api_key import ApiKeyCreateRequest
from app.models.user import User
from app.models.context import Context
from app.models.device import Device
from app.models.sensor import Sensor
from app.models.ingest import Ingest
from app.models.api_key import ApiKey


class AuthControllerInterface(Protocol):
    def login(self, login_request: LoginRequest) -> TokenResponse: ...


class UserControllerInterface(Protocol):
    def create_user(self, create_user_request: UserCreateRequest) -> User: ...


class ContextControllerInterface(Protocol):
    def create(self, req: ContextCreateRequest) -> Context: ...

    def list(self, page: int = 1, limit: int = 10, name: Optional[str] = None) -> Tuple[List[Context], int]: ...

    def get(self, context_id: UUID) -> Context: ...

    def update(self, context_id: UUID, req: ContextUpdateRequest) -> Context: ...

    def delete(self, context_id: UUID) -> None: ...


class DeviceControllerInterface(Protocol):
    """Device controller HTTP orchestration interface."""
    
    def create(self, req: DeviceCreateRequest) -> Device: ...

    def list(
        self, 
        page: int = 1, 
        limit: int = 10,
        name: Optional[str] = None,
        model: Optional[str] = None,
        status: Optional[str] = None,
        context_id: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Device], int]: ...

    def get(self, device_id: UUID) -> Device: ...

    def update(self, device_id: UUID, req: DeviceUpdateRequest) -> Device: ...

    def delete(self, device_id: UUID) -> None: ...


class SensorControllerInterface(Protocol):
    def create(self, req: SensorCreateRequest) -> Sensor: ...

    def list(
        self,
        page: int = 1,
        limit: int = 10,
        name: Optional[str] = None,
        type: Optional[str] = None,
        unit: Optional[str] = None,
        device_id: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Sensor], int]: ...

    def get(self, sensor_id: UUID) -> Sensor: ...

    def update(self, sensor_id: UUID, req: SensorUpdateRequest) -> Sensor: ...

    def delete(self, sensor_id: UUID) -> None: ...


class IngestControllerInterface(Protocol):
    def create(self, req: IngestCreateRequest) -> Ingest: ...

    def list(
        self,
        page: int = 1,
        limit: int = 10,
        sensor_id: Optional[UUID] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Ingest], int]: ...

    def get(self, ingest_id: UUID) -> Ingest: ...

    def update(self, ingest_id: UUID, req: IngestUpdateRequest) -> Ingest: ...

    def delete(self, ingest_id: UUID) -> None: ...


class ApiKeyControllerInterface(Protocol):
    def create(self, user_id: UUID, req: ApiKeyCreateRequest) -> Tuple[ApiKey, str]: ...

    def list(self, user_id: UUID) -> List[ApiKey]: ...

    def revoke(self, api_key_id: UUID, user_id: UUID) -> ApiKey: ...

    def rotate(self, api_key_id: UUID, user_id: UUID) -> Tuple[ApiKey, str]: ...
