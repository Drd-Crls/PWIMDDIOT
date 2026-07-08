import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.settings.database import Base


class Ingest(Base):
    __tablename__ = "ingests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ingest_metadata = Column("metadata", JSONB, nullable=False)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    sensor = relationship("Sensor", backref="ingests")
