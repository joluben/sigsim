"""
SQLAlchemy database models
"""
import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.payload import PayloadType
from app.models.target import TargetType


def generate_uuid():
    return str(uuid.uuid4())


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    devices = relationship("Device", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"


class Device(Base):
    __tablename__ = "devices"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    metadata = Column(JSON, default=dict)
    payload_id = Column(String(36), ForeignKey("payloads.id", ondelete="SET NULL"))
    target_system_id = Column(String(36), ForeignKey("target_systems.id", ondelete="SET NULL"))
    send_interval = Column(Integer, default=10, nullable=False)  # seconds
    is_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="devices")
    payload = relationship("Payload")
    target_system = relationship("TargetSystem")
    
    # Indexes
    __table_args__ = (
        Index('ix_device_project_enabled', 'project_id', 'is_enabled'),
    )
    
    def __repr__(self):
        return f"<Device(id={self.id}, name={self.name}, project_id={self.project_id})>"


class Payload(Base):
    __tablename__ = "payloads"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, index=True)
    type = Column(Enum(PayloadType), nullable=False)
    schema = Column(JSON)  # For visual type
    python_code = Column(Text)  # For python type
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_payload_name_type', 'name', 'type'),
    )
    
    def __repr__(self):
        return f"<Payload(id={self.id}, name={self.name}, type={self.type})>"


class TargetSystem(Base):
    __tablename__ = "target_systems"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, unique=True, index=True)
    type = Column(Enum(TargetType), nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_target_name_type', 'name', 'type'),
    )
    
    def __repr__(self):
        return f"<TargetSystem(id={self.id}, name={self.name}, type={self.type})>"