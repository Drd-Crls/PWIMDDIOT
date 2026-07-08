from typing import Optional, Tuple
from uuid import UUID
from app.models.device import Device
from app.repositories.device_repository import DeviceRepositoryInterface
from app.core.exceptions import ValidationError, NotFoundError, ConflictError
from app.interfaces.services import DeviceServiceInterface
from app.enums.device_status import DeviceStatus


class DeviceService(DeviceServiceInterface):
    """
    Device service business logic implementation.
    
    Responsibilities:
    - Validate business rules before persistence
    - Validate foreign key references (context_id, created_by)
    - Orchestrate repository operations
    - Raise meaningful domain exceptions
    
    Architecture Notes:
    - Receives DeviceRepositoryInterface via dependency injection
    - Validates foreign key references to prevent orphaned relationships
    - Throws custom exceptions, not HTTPException (converts to HTTP in exception handlers)
    - All input validation happens here, not in repository
    """
    
    def __init__(self, device_repository: DeviceRepositoryInterface):
        self.device_repository = device_repository

    def create_device(
        self, 
        name: str, 
        model: str, 
        status: DeviceStatus,
        context_id: UUID,
        created_by: UUID,
        location: Optional[str] = None
    ) -> Device:
        """
        Create a new device with validation.
        
        Validation Rules:
        - name: required, trimmed, max 128 chars
        - model: required, trimmed, max 128 chars
        - status: required, must be valid DeviceStatus enum
        - location: optional, max 256 chars
        - context_id: required, must reference existing context
        - created_by: required, must reference existing user
        
        Note: Foreign key validation happens at repository level
        
        Args:
            name: Device name
            model: Device model
            status: Device status (ACTIVE, INACTIVE, MAINTENANCE, OFFLINE)
            context_id: UUID of context this device belongs to
            created_by: UUID of user creating this device
            location: Optional device location
            
        Returns:
            Persisted Device entity
            
        Raises:
            ValidationError: If required fields are empty or exceed max length
            ConflictError: If context_id or created_by references non-existent entities
        """
        # Validate required fields
        if not name or not name.strip():
            raise ValidationError("'name' is required and cannot be empty")
        if not model or not model.strip():
            raise ValidationError("'model' is required and cannot be empty")
        
        # Validate max lengths
        if len(name.strip()) > 128:
            raise ValidationError("'name' must be at most 128 characters")
        if len(model.strip()) > 128:
            raise ValidationError("'model' must be at most 128 characters")
        if location and len(location) > 256:
            raise ValidationError("'location' must be at most 256 characters")
        
        # Create device entity
        new_device = Device(
            name=name.strip(),
            model=model.strip(),
            location=location,
            status=status,
            context_id=context_id,
            created_by=created_by
        )
        
        # Repository handles FK validation and raises ConflictError if refs don't exist
        return self.device_repository.create(new_device)

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
    ) -> Tuple[list, int]:
        """
        List devices with pagination, filtering, and sorting.
        
        Pagination:
        - page: 1-based page number
        - limit: items per page (1-100)
        
        Filtering:
        - name: Case-insensitive substring match
        - model: Case-insensitive substring match
        - status: Exact match (ACTIVE, INACTIVE, MAINTENANCE, OFFLINE)
        - context_id: Exact match on context
        
        Sorting:
        - sort_by: Column to sort (name, model, status, created_at, updated_at)
        - sort_order: 'asc' or 'desc'
        
        Returns:
            Tuple of (devices list, total count)
            
        Raises:
            ValidationError: If pagination params are invalid
        """
        # Validate pagination
        if page < 1:
            raise ValidationError("'page' must be >= 1")
        if limit < 1 or limit > 100:
            raise ValidationError("'limit' must be between 1 and 100")
        
        # Validate sort_by column
        valid_sort_columns = {"name", "model", "status", "created_at", "updated_at"}
        if sort_by not in valid_sort_columns:
            raise ValidationError(f"'sort_by' must be one of {valid_sort_columns}")
        
        offset = (page - 1) * limit
        items, total = self.device_repository.list(
            offset=offset,
            limit=limit,
            name_filter=name,
            model_filter=model,
            status_filter=status,
            context_id_filter=context_id,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return items, total

    def get_device(self, device_id: UUID) -> Device:
        """
        Fetch device by ID.
        
        Args:
            device_id: UUID of device to fetch
            
        Returns:
            Device entity
            
        Raises:
            NotFoundError: If device not found
        """
        device = self.device_repository.get_by_id(device_id)
        if not device:
            raise NotFoundError("Device not found")
        return device

    def update_device(
        self,
        device_id: UUID,
        name: Optional[str] = None,
        model: Optional[str] = None,
        status: Optional[DeviceStatus] = None,
        location: Optional[str] = None
    ) -> Device:
        """
        Update an existing device.
        
        Update Rules:
        - All fields optional (PATCH-like)
        - If provided, must meet same validation as create
        - updated_at auto-managed by SQLAlchemy
        
        Args:
            device_id: UUID of device to update
            name: New device name (optional)
            model: New device model (optional)
            status: New device status (optional)
            location: New device location (optional)
            
        Returns:
            Updated Device entity
            
        Raises:
            NotFoundError: If device not found
            ValidationError: If provided fields fail validation
        """
        device = self.device_repository.get_by_id(device_id)
        if not device:
            raise NotFoundError("Device not found")
        
        # Validate and update name if provided
        if name is not None:
            if not name.strip():
                raise ValidationError("'name' cannot be empty")
            if len(name.strip()) > 128:
                raise ValidationError("'name' must be at most 128 characters")
            device.name = name.strip()
        
        # Validate and update model if provided
        if model is not None:
            if not model.strip():
                raise ValidationError("'model' cannot be empty")
            if len(model.strip()) > 128:
                raise ValidationError("'model' must be at most 128 characters")
            device.model = model.strip()
        
        # Update status if provided
        if status is not None:
            device.status = status
        
        # Validate and update location if provided
        if location is not None:
            if len(location) > 256:
                raise ValidationError("'location' must be at most 256 characters")
            device.location = location
        
        # updated_at handled by SQLAlchemy onupdate
        return self.device_repository.update(device)

    def delete_device(self, device_id: UUID) -> None:
        """
        Delete a device.
        
        Args:
            device_id: UUID of device to delete
            
        Raises:
            NotFoundError: If device not found
            ConflictError: If device is still referenced by other entities
        """
        device = self.device_repository.get_by_id(device_id)
        if not device:
            raise NotFoundError("Device not found")
        
        # Repository raises ConflictError if FK constraints prevent deletion
        self.device_repository.delete(device)
