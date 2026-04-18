"""
Project Pydantic Schemas

Request/Response models for project CRUD operations.
"""

from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class ProjectBase(BaseModel):
    """Base project fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Project title")
    description: Optional[str] = Field(None, description="Project description")
    emoji: Optional[str] = Field("📁", description="Project emoji icon")
    image_url: Optional[str] = Field(None, description="Project cover image URL")
    status: str = Field("planning", description="Project status: planning, active, paused, completed, archived")
    start_date: date = Field(..., description="Project start date")
    end_date: date = Field(..., description="Project end date")
    total_budget: float = Field(..., gt=0, description="Total project budget")
    currency: str = Field("USD", max_length=10, description="Budget currency")
    
    @field_validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values.data and v < values.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    @field_validator('status')
    def validate_status(cls, v):
        valid_statuses = ['planning', 'active', 'paused', 'completed', 'archived']
        if v not in valid_statuses:
            raise ValueError(f'status must be one of {valid_statuses}')
        return v


class ProjectCreate(ProjectBase):
    """Project creation request"""
    pass


class ProjectUpdate(BaseModel):
    """Project update request - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    emoji: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_budget: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=10)
    
    @field_validator('end_date')
    def validate_dates(cls, v, values):
        if v and 'start_date' in values.data and values.data['start_date']:
            if v < values.data['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


class ProjectResponse(BaseModel):
    """Project response with KPI calculations"""
    id: uuid.UUID
    org_id: uuid.UUID
    title: str
    description: Optional[str]
    emoji: Optional[str]
    image_url: Optional[str]
    status: str
    start_date: date
    end_date: date
    total_budget: float
    currency: str
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    # KPI fields (computed)
    total_spent: float = 0
    bur: float = 0
    bur_status: str = "ok"
    bur_color: str = "green"
    bur_alert: Optional[str] = None
    kar: float = 0
    kar_status: str = "critical"
    kar_color: str = "red"
    bbr: float = 0
    days_to_exhaust: int = 0
    days_elapsed: int = 0
    days_remaining: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    overdue_tasks: int = 0
    completion_rate: float = 0
    member_count: int = 0
    
    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Project list response"""
    total: int
    projects: List[ProjectResponse]