from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Tuple
from app.repositories.device_repository import DeviceRepository
from app.services.device_service import DeviceService
from app.interfaces.services import DeviceServiceInterface
from app.schemas.device import DeviceCreateRequest, DeviceUpdateRequest
from app.interfaces.controllers import DeviceControllerInterface
from app.models.device import Device


class DeviceController(DeviceControllerInterface):
    """
    Device controller HTTP orchestration layer.
    
    Responsibilities:
    - Receive HTTP request DTOs (validated by FastAPI/Pydantic)
    - Orchestrate service calls
    - Return response DTOs
    - Let exceptions bubble to exception handlers
    
    Architecture Notes:
    - Instantiates dependencies via constructor injection
    - Delegates all business logic to service layer
    - Never contains business logic itself
    - No direct database access (uses repositories through service)
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.device_repository = DeviceRepository(db)
        self.device_service: DeviceServiceInterface = DeviceService(self.device_repository)

    def create(self, req: DeviceCreateRequest) -> Device:
        """
        Create device from request DTO.
        
        Delegates to service which:
        - Validates business rules
        - Validates foreign key references
        - Persists to database
        """
        return self.device_service.create_device(
            name=req.name,
            model=req.model,
            status=req.status,
            context_id=req.context_id,
            created_by=req.created_by,
            location=req.location
        )

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
    ) -> Tuple[List[Device], int]:
        """
        List devices with filtering and pagination.
        
        Delegates to service for:
        - Pagination validation
        - Query building and filtering
        - Sorting
        """
        return self.device_service.list_devices(
            page=page,
            limit=limit,
            name=name,
            model=model,
            status=status,
            context_id=context_id,
            sort_by=sort_by,
            sort_order=sort_order
        )

    def get(self, device_id: UUID) -> Device:
        """
        Get device by ID.
        
        Raises NotFoundError if not found (converted to 404 by exception handler)
        """
        return self.device_service.get_device(device_id)

    def update(self, device_id: UUID, req: DeviceUpdateRequest) -> Device:
        """
        Update device from request DTO.
        
        Delegates to service which:
        - Fetches existing device
        - Validates provided fields
        - Updates and persists
        """
        return self.device_service.update_device(
            device_id=device_id,
            name=req.name,
            model=req.model,
            status=req.status,
            location=req.location
        )

    def delete(self, device_id: UUID) -> None:
        """
        Delete device by ID.
        
        Delegates to service which:
        - Fetches existing device
        - Deletes from database
        - Raises ConflictError if referenced by other entities
        """
        return self.device_service.delete_device(device_id)
