"""
KPI Model - Track Key Performance Indicators for projects
"""

import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.session import Base


class KPI(Base):
    __tablename__ = "kpis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # KPI definition
    indicator_name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    target_value = Column(Numeric(15, 2), nullable=False)
    unit = Column(String(50), nullable=True)  # %, count, rating, etc.
    
    # Current status
    actual_value = Column(Numeric(15, 2), nullable=True, default=0)
    kar = Column(Numeric(5, 2), nullable=True)  # KPI Achievement Ratio
    status = Column(String(20), nullable=True)  # critical, warning, satisfactory, good
    
    # Period tracking
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", backref="kpis")
    creator = relationship("User", foreign_keys=[created_by])