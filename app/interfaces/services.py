from __future__ import annotations
from typing import Protocol, Optional, Tuple, Dict, Any, List
from uuid import UUID
from datetime import timedelta, datetime
from decimal import Decimal

from app.schemas.auth import TokenResponse
from app.schemas.api_key import ApiKeyContext
from app.models.context import Context
from app.models.user import User
from app.models.device import Device
from app.models.sensor import Sensor
from app.models.ingest import Ingest
from app.models.api_key import ApiKey
from app.enums.device_status import DeviceStatus


class TokenServiceInterface(Protocol):
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str: ...

    @staticmethod
    def decode_token(token: str) -> Optional[dict]: ...


class AuthServiceInterface(Protocol):
    def login(self, email: str, password: str) -> TokenResponse: ...


class UserServiceInterface(Protocol):
    def create_user(self, email: str, password: str, role: str, name: str) -> User: ...


class ContextServiceInterface(Protocol):
    def create_context(self, name: str, description: Optional[str] = None) -> Context: ...

    def list_contexts(self, page: int = 1, limit: int = 10, name: Optional[str] = None) -> Tuple[list, int]: ...

    def get_context(self, context_id: UUID) -> Context: ...

    def update_context(self, context_id: UUID, name: Optional[str] = None, description: Optional[str] = None) -> Context: ...

    def delete_context(self, context_id: UUID) -> None: ...


class DeviceServiceInterface(Protocol):
    """Device service business logic interface."""
    
    def create_device(
        self, 
        name: str, 
        model: str, 
        status: DeviceStatus,
        context_id: UUID,
        created_by: UUID,
        location: Optional[str] = None
    ) -> Device: ...

    def list_devices(
        self, 
        page: int = 1, 
        limit: int = 10,
        name: Optional[str] = None,
        model: Optional[str] = None,
        status: Optional[str] = None,
        context_id: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[list, int]: ...

    def get_device(self, device_id: UUID) -> Device: ...

    def update_device(
        self,
        device_id: UUID,
        name: Optional[str] = None,
        model: Optional[str] = None,
        status: Optional[DeviceStatus] = None,
        location: Optional[str] = None
    ) -> Device: ...

    def delete_device(self, device_id: UUID) -> None: ...


class SensorServiceInterface(Protocol):
    def create_sensor(
        self,
        name: str,
        type: str,
        device_id: UUID,
        unit: Optional[str] = None,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
    ) -> Sensor: ...

    def list_sensors(
        self,
        page: int = 1,
        limit: int = 10,
        name: Optional[str] = None,
        type: Optional[str] = None,
        unit: Optional[str] = None,
        device_id: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[list, int]: ...

    def get_sensor(self, sensor_id: UUID) -> Sensor: ...

    def update_sensor(
        self,
        sensor_id: UUID,
        name: Optional[str] = None,
        type: Optional[str] = None,
        unit: Optional[str] = None,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
        device_id: Optional[UUID] = None,
    ) -> Sensor: ...

    def delete_sensor(self, sensor_id: UUID) -> None: ...


class IngestServiceInterface(Protocol):
    def create_ingest(self, metadata: Dict[str, Any], sensor_id: UUID) -> Ingest: ...

    def list_ingests(
        self,
        page: int = 1,
        limit: int = 10,
        sensor_id: Optional[UUID] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[list, int]: ...

    def get_ingest(self, ingest_id: UUID) -> Ingest: ...

    def update_ingest(
        self,
        ingest_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        sensor_id: Optional[UUID] = None,
    ) -> Ingest: ...

    def delete_ingest(self, ingest_id: UUID) -> None: ...


class ApiKeyGeneratorInterface(Protocol):
    def generate(self) -> str: ...

    def hash(self, raw_key: str) -> str: ...

    def verify(self, raw_key: str, key_hash: str) -> bool: ...


class ApiKeyServiceInterface(Protocol):
    def create_api_key(
        self, user_id: UUID, permissions: Dict[str, List[str]]
    ) -> Tuple[ApiKey, str]: ...

    def list_api_keys(self, user_id: UUID) -> List[ApiKey]: ...

    def get_api_key(self, api_key_id: UUID, user_id: UUID) -> ApiKey: ...

    def revoke_api_key(self, api_key_id: UUID, user_id: UUID) -> ApiKey: ...

    def rotate_api_key(self, api_key_id: UUID, user_id: UUID) -> Tuple[ApiKey, str]: ...

    def authenticate(self, raw_key: str) -> ApiKeyContext: ...
