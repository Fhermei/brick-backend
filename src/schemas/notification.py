"""
Notification Pydantic Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    message: str
    data: Optional[dict]
    is_read: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    notifications: list[NotificationResponse]


class MarkReadRequest(BaseModel):
    notification_ids: list[uuid.UUID]