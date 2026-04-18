"""
Report Pydantic Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ReportGenerateRequest(BaseModel):
    type: str = Field(..., description="organization, project, financial, kpi")
    org_id: uuid.UUID = Field(...)
    project_id: Optional[uuid.UUID] = Field(None)
    date_from: Optional[datetime] = Field(None)
    date_to: Optional[datetime] = Field(None)
    
    @field_validator('date_from', 'date_to', mode='before')
    @classmethod
    def parse_date(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            # Try to parse as date first, then datetime
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Parse as date and convert to datetime
                    d = date.fromisoformat(value)
                    return datetime(d.year, d.month, d.day)
                except ValueError:
                    return None
        return value
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }