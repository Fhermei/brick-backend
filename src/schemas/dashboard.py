"""
Dashboard Pydantic Schemas

Response models for dashboard statistics, recent projects, and recent tasks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class TaskStats(BaseModel):
    """Task statistics for dashboard"""
    total_tasks: int = Field(..., description="Total number of tasks")
    overdue_tasks: int = Field(..., description="Number of overdue tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    completion_rate: float = Field(..., description="Task completion rate percentage")


class BudgetStats(BaseModel):
    """Budget statistics for dashboard"""
    total_budget: float = Field(..., description="Total budget amount")
    total_spent: float = Field(..., description="Total amount spent")
    remaining_budget: float = Field(..., description="Remaining budget amount")
    bur: float = Field(..., description="Budget Utilisation Rate percentage")
    bur_status: str = Field(..., description="BUR status: ok, alert, critical")
    bur_color: str = Field(..., description="BUR color indicator")
    bur_alert: Optional[str] = Field(None, description="BUR alert message if any")
    bbr: float = Field(..., description="Budget Burn Rate per day")
    days_to_exhaust: int = Field(..., description="Days until budget exhausted")


class KPIStats(BaseModel):
    """KPI statistics for dashboard"""
    average_kar: float = Field(..., description="Average KPI Achievement Ratio")
    kar_status: str = Field(..., description="KAR status: critical, warning, satisfactory, good")
    kar_color: str = Field(..., description="KAR color indicator")
    kar_label: str = Field(..., description="KAR status label")


class DashboardStats(BaseModel):
    """Complete dashboard statistics response"""
    organization_id: uuid.UUID
    organization_name: str
    task_stats: TaskStats
    budget_stats: BudgetStats
    kpi_stats: KPIStats
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RecentProjectRow(BaseModel):
    """Recent project row for dashboard table"""
    id: uuid.UUID
    title: str
    emoji: Optional[str]
    bur: float
    bur_status: str
    kar: float
    kar_status: str
    team_members: List[dict]
    updated_at: datetime


class RecentTaskRow(BaseModel):
    """Recent task row for dashboard table"""
    id: uuid.UUID
    title: str
    project_id: uuid.UUID
    project_title: str
    priority: str
    priority_color: str
    status: str
    due_date: date
    is_overdue: bool
    assigned_to_name: Optional[str]
    assigned_to_avatar: Optional[str]


class RecentProjectsResponse(BaseModel):
    """Recent projects response"""
    projects: List[RecentProjectRow]
    total: int


class RecentTasksResponse(BaseModel):
    """Recent tasks response"""
    tasks: List[RecentTaskRow]
    total: int