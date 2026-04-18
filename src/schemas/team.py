"""
Team Pydantic Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class InviteRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address of the person to invite")
    role_name: Optional[str] = Field("member", description="Role name for the user")
    role_id: Optional[uuid.UUID] = Field(None, description="Role ID (optional)")


class InviteResponse(BaseModel):
    message: str
    email: str
    invited_at: datetime


class MemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    email: str
    role: str
    role_id: Optional[uuid.UUID]
    status: str
    joined_at: datetime
    avatar: Optional[str] = None


class UpdateMemberRole(BaseModel):
    role_name: Optional[str] = None
    role_id: Optional[uuid.UUID] = None


class TeamListResponse(BaseModel):
    total: int
    members: List[MemberResponse]