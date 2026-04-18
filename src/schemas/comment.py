"""
Comment Pydantic Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class CommentCreate(BaseModel):
    body: str
    parent_id: Optional[uuid.UUID] = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    user_email: str
    body: str
    parent_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    replies: List["CommentResponse"] = []
    
    model_config = {"from_attributes": True}


CommentResponse.model_rebuild()