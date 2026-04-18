"""
KPI Pydantic Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class KPICreate(BaseModel):
    indicator_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_value: float = Field(..., gt=0)
    unit: Optional[str] = None
    period_start: date = Field(...)
    period_end: date = Field(...)


class KPIUpdate(BaseModel):
    actual_value: float = Field(..., ge=0)


class KPIResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    project_title: str
    indicator_name: str
    description: Optional[str]
    target_value: float
    actual_value: Optional[float]
    kar: Optional[float]
    status: Optional[str]
    unit: Optional[str]
    period_start: date
    period_end: date
    created_by: uuid.UUID
    created_by_name: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class KPIListResponse(BaseModel):
    total: int
    kpis: list[KPIResponse]