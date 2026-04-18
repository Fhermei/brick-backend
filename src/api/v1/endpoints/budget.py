"""
Budget API Endpoints - Get budget summaries
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
import uuid

from src.core.security import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.models.organization import Organization, OrgMember
from src.models.project import Project
from src.models.task import Task
from src.models.expense import Expense
from src.schemas.budget import BudgetSummaryResponse, ProjectBudgetResponse, ProjectBudgetListResponse
from src.core.kpi import compute_bur, compute_bbr, compute_days_to_exhaust, get_bur_status, calculate_days_elapsed

router = APIRouter()


def check_org_access(user_id: uuid.UUID, org_id: uuid.UUID, db: Session) -> bool:
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id,
        OrgMember.status == "active"
    ).first()
    return membership is not None


@router.get("/summary", response_model=BudgetSummaryResponse)
async def get_budget_summary(
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall budget summary for an organization"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check access
    if not check_org_access(user.id, org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get all projects
    projects = db.query(Project).filter(Project.org_id == org_id, Project.status != "archived").all()
    
    # Calculate totals
    total_budget = sum(float(p.total_budget) for p in projects)
    
    # Get all approved expenses
    expenses = db.query(Expense).join(Task).filter(
        Expense.status == "approved",
        Task.project_id.in_([p.id for p in projects])
    ).all()
    total_spent = sum(float(e.amount) for e in expenses)
    
    remaining_budget = total_budget - total_spent
    bur = compute_bur(total_spent, total_budget) if total_budget > 0 else 0
    bur_info = get_bur_status(bur)
    
    # Calculate BBR (Budget Burn Rate)
    # Use organization creation date as start
    days_elapsed = calculate_days_elapsed(org.created_at.date())
    bbr = compute_bbr(total_spent, days_elapsed) if days_elapsed > 0 else 0
    days_to_exhaust = compute_days_to_exhaust(remaining_budget, bbr) if bbr > 0 else 999
    
    # Get task stats
    tasks = db.query(Task).join(Project).filter(Project.org_id == org_id, Task.is_deleted == False).all()
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "completed"])
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return BudgetSummaryResponse(
        org_id=org.id,
        org_name=org.name,
        currency=org.currency,
        total_budget=total_budget,
        total_spent=total_spent,
        remaining_budget=remaining_budget,
        bur=bur,
        bur_status=bur_info["status"],
        bur_color=bur_info["color"],
        bur_alert=bur_info.get("alert"),
        bbr=bbr,
        days_to_exhaust=days_to_exhaust,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        completion_rate=completion_rate
    )


@router.get("/project/{project_id}", response_model=ProjectBudgetResponse)
async def get_project_budget(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget summary for a specific project"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    if not check_org_access(user.id, project.org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get approved expenses for this project
    expenses = db.query(Expense).join(Task).filter(
        Expense.status == "approved",
        Task.project_id == project_id
    ).all()
    total_spent = sum(float(e.amount) for e in expenses)
    
    bur = compute_bur(total_spent, float(project.total_budget)) if project.total_budget > 0 else 0
    bur_info = get_bur_status(bur)
    
    remaining_budget = float(project.total_budget) - total_spent
    
    # Get task stats
    tasks = db.query(Task).filter(Task.project_id == project_id, Task.is_deleted == False).all()
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "completed"])
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return ProjectBudgetResponse(
        project_id=project.id,
        project_title=project.title,
        project_status=project.status,
        total_budget=float(project.total_budget),
        total_spent=total_spent,
        remaining_budget=remaining_budget,
        bur=bur,
        bur_status=bur_info["status"],
        task_count=total_tasks,
        completed_task_count=completed_tasks,
        completion_rate=completion_rate
    )


@router.get("/projects", response_model=ProjectBudgetListResponse)
async def list_project_budgets(
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget summary for all projects in an organization"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check access
    if not check_org_access(user.id, org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all projects
    projects = db.query(Project).filter(Project.org_id == org_id, Project.status != "archived").all()
    
    project_responses = []
    for project in projects:
        # Get approved expenses
        expenses = db.query(Expense).join(Task).filter(
            Expense.status == "approved",
            Task.project_id == project.id
        ).all()
        total_spent = sum(float(e.amount) for e in expenses)
        
        bur = compute_bur(total_spent, float(project.total_budget)) if project.total_budget > 0 else 0
        bur_info = get_bur_status(bur)
        
        # Get task stats
        tasks = db.query(Task).filter(Task.project_id == project.id, Task.is_deleted == False).all()
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == "completed"])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        project_responses.append(ProjectBudgetResponse(
            project_id=project.id,
            project_title=project.title,
            project_status=project.status,
            total_budget=float(project.total_budget),
            total_spent=total_spent,
            remaining_budget=float(project.total_budget) - total_spent,
            bur=bur,
            bur_status=bur_info["status"],
            task_count=total_tasks,
            completed_task_count=completed_tasks,
            completion_rate=completion_rate
        ))
    
    return ProjectBudgetListResponse(total=len(project_responses), projects=project_responses)