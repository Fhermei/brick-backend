"""
Budget Pydantic Schemas
"""

from __future__ import annotations

import uuid
from typing import Optional
from pydantic import BaseModel


class BudgetSummaryResponse(BaseModel):
    org_id: uuid.UUID
    org_name: str
    currency: str
    total_budget: float
    total_spent: float
    remaining_budget: float
    bur: float  # Budget Utilisation Rate
    bur_status: str  # ok, alert, critical
    bur_color: str
    bur_alert: Optional[str]
    bbr: float  # Budget Burn Rate
    days_to_exhaust: int
    total_tasks: int
    completed_tasks: int
    completion_rate: float


class ProjectBudgetResponse(BaseModel):
    project_id: uuid.UUID
    project_title: str
    project_status: str
    total_budget: float
    total_spent: float
    remaining_budget: float
    bur: float
    bur_status: str
    task_count: int
    completed_task_count: int
    completion_rate: float


class ProjectBudgetListResponse(BaseModel):
    total: int
    projects: list[ProjectBudgetResponse]