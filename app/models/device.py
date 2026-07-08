import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.settings.database import Base
from app.enums.device_status import DeviceStatus


class Device(Base):
    """
    Device entity representing an IoT device in the system.
    
    Architecture Notes:
    - Inherits from SQLAlchemy Base for ORM mapping
    - UUID primary key for distributed system compatibility
    - Foreign keys reference Context and User entities
    - Timestamps auto-managed by SQLAlchemy (created_at, updated_at)
    - DeviceStatus enum enforces valid status values at database level
    """
    __tablename__ = "devices"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core Fields
    name = Column(String(128), nullable=False, index=True)
    model = Column(String(128), nullable=False)
    location = Column(String(256), nullable=True)
    status = Column(Enum(DeviceStatus), nullable=False, default=DeviceStatus.INACTIVE)
    
    # Foreign Keys - references to other entities
    context_id = Column(UUID(as_uuid=True), ForeignKey("contexts.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps - auto-managed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
