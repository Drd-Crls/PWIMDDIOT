from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from app.models.user import User
from app.models.context import Context
from app.models.device import Device
from app.models.sensor import Sensor
from app.models.ingest import Ingest
from app.models.api_key import ApiKey


class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass


class ContextRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, context_id: UUID) -> Optional[Context]:
        pass

    @abstractmethod
    def list(self, offset: int, limit: int, name_filter: Optional[str] = None) -> Tuple[List[Context], int]:
        pass

    @abstractmethod
    def create(self, context: Context) -> Context:
        pass

    @abstractmethod
    def update(self, context: Context) -> Context:
        pass

    @abstractmethod
    def delete(self, context: Context) -> None:
        pass


class DeviceRepositoryInterface(ABC):
    """
    Device data access interface.
    
    Contract:
    - All operations are abstracted behind this interface
    - Implementations must handle database errors and convert to AppException subclasses
    - Foreign key validation happens in Service layer, not Repository
    """
    @abstractmethod
    def get_by_id(self, device_id: UUID) -> Optional[Device]:
        """Fetch device by ID. Returns None if not found."""
        pass

    @abstractmethod
    def list(
        self, 
        offset: int, 
        limit: int, 
        name_filter: Optional[str] = None,
        model_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        context_id_filter: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Device], int]:
        """
        List devices with pagination, filtering, and sorting.
        
        Returns: (items, total_count)
        """
        pass

    @abstractmethod
    def create(self, device: Device) -> Device:
        """Create a new device. Raises DatabaseError on constraint violations."""
        pass

    @abstractmethod
    def update(self, device: Device) -> Device:
        """Update an existing device. Raises DatabaseError on constraint violations."""
        pass

    @abstractmethod
    def delete(self, device: Device) -> None:
        """Delete a device. Raises DatabaseError on FK constraint violations."""
        pass


class SensorRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, sensor_id: UUID) -> Optional[Sensor]:
        pass

    @abstractmethod
    def list(
        self,
        offset: int,
        limit: int,
        name_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        unit_filter: Optional[str] = None,
        device_id_filter: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Sensor], int]:
        pass

    @abstractmethod
    def create(self, sensor: Sensor) -> Sensor:
        pass

    @abstractmethod
    def update(self, sensor: Sensor) -> Sensor:
        pass

    @abstractmethod
    def delete(self, sensor: Sensor) -> None:
        pass


class IngestRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, ingest_id: UUID) -> Optional[Ingest]:
        pass

    @abstractmethod
    def list(
        self,
        offset: int,
        limit: int,
        sensor_id_filter: Optional[UUID] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Ingest], int]:
        pass

    @abstractmethod
    def create(self, ingest: Ingest) -> Ingest:
        pass

    @abstractmethod
    def update(self, ingest: Ingest) -> Ingest:
        pass

    @abstractmethod
    def delete(self, ingest: Ingest) -> None:
        pass


class ApiKeyRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, api_key_id: UUID) -> Optional[ApiKey]:
        pass

    @abstractmethod
    def get_by_hash(self, key_hash: str) -> Optional[ApiKey]:
        pass

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> List[ApiKey]:
        pass

    @abstractmethod
    def create(self, api_key: ApiKey) -> ApiKey:
        pass

    @abstractmethod
    def update(self, api_key: ApiKey) -> ApiKey:
        pass
