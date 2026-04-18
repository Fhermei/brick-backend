"""
Task Pydantic Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: str = Field("task", description="task, bug, feature, research")
    priority: str = Field("medium", description="urgent, high, medium, low")
    status: str = Field("todo", description="todo, in_progress, review, to_be_tested, completed, blocked")
    due_date: date = Field(...)
    budget_allocated: Optional[float] = Field(0, ge=0)
    parent_task_id: Optional[uuid.UUID] = None
    custom_fields: Optional[dict] = None


class TaskCreate(TaskBase):
    assigned_to: Optional[uuid.UUID] = None
    additional_assignees: Optional[List[uuid.UUID]] = []
    supervisors: Optional[List[uuid.UUID]] = []


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    budget_allocated: Optional[float] = Field(None, ge=0)
    assigned_to: Optional[uuid.UUID] = None
    additional_assignees: Optional[List[uuid.UUID]] = None
    supervisors: Optional[List[uuid.UUID]] = None
    status: Optional[str] = None
    custom_fields: Optional[dict] = None


class TaskStatusUpdate(BaseModel):
    status: str = Field(..., description="New status for the task")
    blocked_reason: Optional[str] = Field(None, description="Reason if status is blocked")


class TaskBudgetItemCreate(BaseModel):
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    description: Optional[str] = None
    receipt_url: Optional[str] = None


class TaskBudgetItemResponse(BaseModel):
    id: uuid.UUID
    amount: float
    category: str
    description: Optional[str]
    receipt_url: Optional[str]
    is_approved: bool
    user_name: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class TaskAssigneeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    email: str
    is_supervisor: bool
    assigned_at: datetime


class TaskResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    project_title: str
    parent_task_id: Optional[uuid.UUID]
    parent_task_title: Optional[str]
    title: str
    description: Optional[str]
    type: str
    priority: str
    status: str
    assigned_to: Optional[uuid.UUID]
    assigned_to_name: Optional[str]
    date_assigned: datetime
    due_date: date
    completed_at: Optional[datetime]
    budget_allocated: float
    total_spent: float
    blocked_reason: Optional[str]
    is_deleted: bool
    created_by: uuid.UUID
    created_by_name: str
    created_at: datetime
    updated_at: datetime
    additional_assignees: List[TaskAssigneeResponse] = []
    subtasks: List["TaskResponse"] = []
    budget_items: List[TaskBudgetItemResponse] = []
    custom_fields: Optional[dict]
    is_overdue: bool = False
    
    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    total: int
    tasks: List[TaskResponse]


TaskResponse.model_rebuild()