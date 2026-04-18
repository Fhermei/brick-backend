"""
Audit Pydantic Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    action: str
    entity_type: str
    entity_id: Optional[uuid.UUID]
    old_values: Optional[dict]
    new_values: Optional[dict]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    total: int
    logs: list[AuditLogResponse]