from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.device import Device
from app.core.exceptions import DatabaseError, ConflictError
from app.interfaces.repositories import DeviceRepositoryInterface


class DeviceRepository(DeviceRepositoryInterface):
    """
    Device repository implementation.
    
    Responsibilities:
    - Data access for Device entity
    - Database error handling and conversion to AppException subclasses
    - Query building for filtering, sorting, and pagination
    - Transaction management (commit, rollback, refresh)
    
    Architecture Notes:
    - Only layer that directly interacts with SQLAlchemy session
    - Converts database errors to domain exceptions for upper layers
    - Implements DeviceRepositoryInterface for dependency inversion
    - Supports rich filtering (by name, model, status, context_id)
    - Supports custom sorting
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, device_id: UUID) -> Optional[Device]:
        """
        Fetch device by ID.
        
        Args:
            device_id: UUID of the device to fetch
            
        Returns:
            Device object or None if not found
        """
        return self.db.query(Device).filter(Device.id == device_id).first()

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
        
        Filtering:
        - name_filter: Case-insensitive substring match on device name
        - model_filter: Case-insensitive substring match on device model
        - status_filter: Exact match on device status (ACTIVE, INACTIVE, MAINTENANCE, OFFLINE)
        - context_id_filter: Exact match on context_id (foreign key)
        
        Sorting:
        - sort_by: Column to sort by (name, model, status, created_at, updated_at)
        - sort_order: 'asc' or 'desc'
        
        Returns:
            Tuple of (devices list, total count before pagination)
        """
        query = self.db.query(Device)
        
        # Apply filters
        if name_filter:
            query = query.filter(Device.name.ilike(f"%{name_filter}%"))
        if model_filter:
            query = query.filter(Device.model.ilike(f"%{model_filter}%"))
        if status_filter:
            query = query.filter(Device.status == status_filter)
        if context_id_filter:
            query = query.filter(Device.context_id == context_id_filter)
        
        # Get total before pagination
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(Device, sort_by, Device.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # Apply pagination
        items = query.offset(offset).limit(limit).all()
        
        return items, total

    def create(self, device: Device) -> Device:
        """
        Create a new device.
        
        Args:
            device: Device entity to persist
            
        Returns:
            Persisted device with ID and timestamps
            
        Raises:
            DatabaseError: On database constraint violations
            ConflictError: On foreign key constraint violations (referenced entity doesn't exist)
        """
        try:
            self.db.add(device)
            self.db.commit()
            self.db.refresh(device)
            return device
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            
            # Check for foreign key constraint violations
            if "context_id" in error_msg and "fk" in error_msg.lower():
                raise ConflictError("Referenced context does not exist")
            if "created_by" in error_msg and "fk" in error_msg.lower():
                raise ConflictError("Referenced user does not exist")
            
            raise DatabaseError(f"Database integrity error: {error_msg}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))

    def update(self, device: Device) -> Device:
        """
        Update an existing device.
        
        Args:
            device: Device entity with updated fields
            
        Returns:
            Updated device with refreshed data from database
            
        Raises:
            DatabaseError: On database constraint violations
        """
        try:
            self.db.add(device)
            self.db.commit()
            self.db.refresh(device)
            return device
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))

    def delete(self, device: Device) -> None:
        """
        Delete a device from database.
        
        Args:
            device: Device entity to delete
            
        Raises:
            DatabaseError: On constraint violations (e.g., if future relations exist)
            ConflictError: On foreign key constraint violations (device still referenced)
        """
        try:
            self.db.delete(device)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise ConflictError("Cannot delete device: it is referenced by other entities")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(str(e))
