"""
Report Model - Store generated report metadata
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from src.db.session import Base


class ReportType(str, enum.Enum):
    ORGANIZATION = "organization"
    PROJECT = "project"
    FINANCIAL = "financial"
    KPI = "kpi"


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    type = Column(SQLEnum(ReportType), nullable=False)
    title = Column(String(200), nullable=False)
    s3_url = Column(Text, nullable=False)
    file_size = Column(String(50), nullable=True)
    
    date_from = Column(DateTime, nullable=True)
    date_to = Column(DateTime, nullable=True)
    
    parameters = Column(JSON, nullable=True)  
    
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", backref="reports")
    project = relationship("Project", backref="reports")
    generator = relationship("User", foreign_keys=[generated_by])