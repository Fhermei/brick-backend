"""
Pydantic schemas for the Organization endpoints.

Request  schemas  — validate what the client sends IN.
Response schemas  — shape what the API sends BACK.

We keep them separate so we never accidentally expose fields
(like owner_id or internal flags) that the client should not see.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Shared base — fields used in both create and update
# ---------------------------------------------------------------------------

class OrgBase(BaseModel):
    name:     str          = Field(..., min_length=2, max_length=200, examples=["Red Cross Lagos"])
    industry: Optional[str] = Field(None, max_length=100, examples=["NGO"])
    currency: str          = Field("USD", max_length=10,  examples=["NGN"])
    timezone: str          = Field("UTC", max_length=100, examples=["Africa/Lagos"])


# ---------------------------------------------------------------------------
# POST /organizations  — create a new organisation
# ---------------------------------------------------------------------------

class OrgCreate(OrgBase):
    """
    Everything required to create a brand-new organisation.
    logo_url is optional at creation time — user can upload later in Settings.
    """
    logo_url: Optional[str] = Field(None, examples=["https://s3.amazonaws.com/brick/logos/abc.png"])


# ---------------------------------------------------------------------------
# PATCH /organizations/:id  — update an existing organisation
# ---------------------------------------------------------------------------

class OrgUpdate(BaseModel):
    """
    All fields are optional — only the ones sent will be updated (partial update).
    """
    name:     Optional[str] = Field(None, min_length=2, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


# ---------------------------------------------------------------------------
# Response — what the API returns for a single organisation
# ---------------------------------------------------------------------------

class OrgMemberResponse(BaseModel):
    """Lightweight member row embedded in OrgResponse."""
    user_id:  uuid.UUID
    role:     str
    status:   str
    joined_at: datetime

    model_config = {"from_attributes": True}


class OrgResponse(BaseModel):
    """
    Full organisation object returned to the client.
    Includes the member count so the frontend can display it without a second call.
    """
    id:          uuid.UUID
    name:        str
    industry:    Optional[str]
    currency:    str
    timezone:    str
    logo_url:    Optional[str]
    owner_id:    uuid.UUID
    is_active:   bool
    created_at:  datetime
    updated_at:  datetime
    member_count: int = 0         # computed in the endpoint, not stored in the DB

    model_config = {"from_attributes": True}


class OrgListResponse(BaseModel):
    """Wraps a list of orgs with a total count."""
    total:         int
    organizations: list[OrgResponse]