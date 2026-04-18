"""
Dashboard API Endpoints

Provides aggregated statistics for the dashboard including:
- Task statistics (total, overdue, completed)
- Budget statistics (BUR, BBR, days to exhaust)
- KPI statistics (average KAR)
- Recent projects and tasks
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import date, datetime
import uuid

from src.core.security import get_current_user
from src.core.kpi import (
    compute_bur, get_bur_status, compute_bbr, compute_days_to_exhaust,
    get_kar_status, aggregate_org_kpis, calculate_days_elapsed
)
from src.db.session import get_db
from src.models.user import User
from src.models.organization import Organization, OrgMember
from src.models.project import Project, ProjectMember
from src.models.task import Task
from src.models.expense import Expense
from src.schemas.dashboard import (
    DashboardStats, TaskStats, BudgetStats, KPIStats,
    RecentProjectsResponse, RecentProjectRow, RecentTasksResponse, RecentTaskRow
)

router = APIRouter()


def get_user_by_claims(claims: dict, db: Session) -> User:
    """Get or create user from JWT claims"""
    email = claims.get("email") or claims.get("username")
    cognito_sub = claims.get("sub")
    
    print(f"Looking up user - Email: {email}, Cognito Sub: {cognito_sub}", flush=True)
    
    # Try to find by cognito_sub first
    user = None
    if cognito_sub:
        user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
        if user:
            print(f"Found user by cognito_sub: {user.id} - {user.email}", flush=True)
    
    # If not found, try by email
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"Found user by email: {user.id} - {user.email}", flush=True)
    
    # If still not found, create the user
    if not user:
        print(f"Creating new user for email: {email}", flush=True)
        user = User(
            name=email.split('@')[0] if email else "Unknown",
            email=email if email else f"{cognito_sub}@temp.com",
            cognito_sub=cognito_sub,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user with ID: {user.id}", flush=True)
    
    return user


def check_org_membership(user_id: uuid.UUID, org_id: uuid.UUID, db: Session) -> bool:
    """Check if user is a member of the organization"""
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id,
        OrgMember.status == "active"
    ).first()
    return membership is not None


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete dashboard statistics for an organization.
    """
    # Get or create user
    user = get_user_by_claims(current_user, db)
    
    # Check if user belongs to the organization
    if not check_org_membership(user.id, org_id, db):
        # Get all organizations the user is a member of for debugging
        user_orgs = db.query(OrgMember).filter(
            OrgMember.user_id == user.id,
            OrgMember.status == "active"
        ).all()
        org_ids = [str(m.org_id) for m in user_orgs]
        print(f"User {user.email} is member of orgs: {org_ids}", flush=True)
        print(f"Requested org: {org_id}", flush=True)
        raise HTTPException(
            status_code=403, 
            detail=f"Access denied. User is not a member of organization {org_id}. User is member of: {org_ids}"
        )
    
    # Get organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get all projects for this organization
    projects = db.query(Project).filter(
        Project.org_id == org_id,
        Project.status != "archived"
    ).all()
    
    # Get all tasks for these projects
    project_ids = [p.id for p in projects]
    tasks = []
    expenses = []
    
    if project_ids:
        tasks = db.query(Task).filter(Task.project_id.in_(project_ids), Task.is_deleted == False).all()
        task_ids = [t.id for t in tasks]
        if task_ids:
            expenses = db.query(Expense).filter(
                Expense.task_id.in_(task_ids),
                Expense.status == "approved"
            ).all()
    
    # Calculate task statistics
    total_tasks = len(tasks)
    today = date.today()
    overdue_tasks = sum(1 for t in tasks if t.due_date and t.due_date < today and t.status != "completed")
    completed_tasks = sum(1 for t in tasks if t.status == "completed")
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate budget statistics
    total_budget = sum(float(p.total_budget) for p in projects)
    total_spent = sum(float(e.amount) for e in expenses)
    remaining_budget = total_budget - total_spent
    bur = compute_bur(total_spent, total_budget)
    bur_info = get_bur_status(bur)
    
    # Calculate BBR (simplified - using org creation date as start)
    days_elapsed = calculate_days_elapsed(org.created_at.date())
    bbr = compute_bbr(total_spent, days_elapsed) if days_elapsed > 0 else 0
    days_to_exhaust = compute_days_to_exhaust(remaining_budget, bbr) if bbr > 0 else 999
    
    # Calculate average KAR from projects
    kar_values = []
    for project in projects:
        project_tasks = [t for t in tasks if t.project_id == project.id]
        project_completed = sum(1 for t in project_tasks if t.status == "completed")
        kar = (project_completed / len(project_tasks) * 100) if project_tasks else 0
        if kar > 0:
            kar_values.append(kar)
    
    avg_kar = sum(kar_values) / len(kar_values) if kar_values else 0
    kar_info = get_kar_status(avg_kar)
    
    return DashboardStats(
        organization_id=org_id,
        organization_name=org.name,
        task_stats=TaskStats(
            total_tasks=total_tasks,
            overdue_tasks=overdue_tasks,
            completed_tasks=completed_tasks,
            completion_rate=round(completion_rate, 2)
        ),
        budget_stats=BudgetStats(
            total_budget=round(total_budget, 2),
            total_spent=round(total_spent, 2),
            remaining_budget=round(remaining_budget, 2),
            bur=bur,
            bur_status=bur_info["status"],
            bur_color=bur_info["color"],
            bur_alert=bur_info.get("alert"),
            bbr=bbr,
            days_to_exhaust=days_to_exhaust
        ),
        kpi_stats=KPIStats(
            average_kar=round(avg_kar, 2),
            kar_status=kar_info["status"],
            kar_color=kar_info["color"],
            kar_label=kar_info["label"]
        ),
        updated_at=datetime.utcnow()
    )


@router.get("/recent-projects", response_model=RecentProjectsResponse)
async def get_recent_projects(
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    limit: int = Query(5, ge=1, le=20, description="Number of projects to return"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent projects for the dashboard.
    """
    # Get or create user
    user = get_user_by_claims(current_user, db)
    
    # Check organization access
    if not check_org_membership(user.id, org_id, db):
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    # Get recent projects
    projects = db.query(Project).filter(
        Project.org_id == org_id,
        Project.status != "archived"
    ).order_by(Project.updated_at.desc()).limit(limit).all()
    
    # Get all tasks for these projects
    project_ids = [p.id for p in projects]
    tasks = []
    expenses = []
    
    if project_ids:
        tasks = db.query(Task).filter(Task.project_id.in_(project_ids), Task.is_deleted == False).all()
        task_ids = [t.id for t in tasks]
        if task_ids:
            expenses = db.query(Expense).filter(Expense.task_id.in_(task_ids), Expense.status == "approved").all()
    
    # Build response
    recent_projects = []
    for project in projects:
        project_tasks = [t for t in tasks if t.project_id == project.id]
        project_expenses = [e for e in expenses if e.task_id in [t.id for t in project_tasks]]
        
        total_spent = sum(float(e.amount) for e in project_expenses)
        bur = compute_bur(total_spent, float(project.total_budget))
        bur_info = get_bur_status(bur)
        
        completed_tasks = sum(1 for t in project_tasks if t.status == "completed")
        kar = (completed_tasks / len(project_tasks) * 100) if project_tasks else 0
        kar_info = get_kar_status(kar)
        
        # Get team members
        project_members = db.query(ProjectMember).filter(ProjectMember.project_id == project.id).limit(3).all()
        team_members = []
        for pm in project_members:
            member = db.query(User).filter(User.id == pm.user_id).first()
            if member:
                team_members.append({
                    "name": member.name,
                    "initial": member.name[0] if member.name else "U"
                })
        
        recent_projects.append(RecentProjectRow(
            id=project.id,
            title=project.title,
            emoji=project.emoji,
            bur=bur,
            bur_status=bur_info["status"],
            kar=kar,
            kar_status=kar_info["status"],
            team_members=team_members,
            updated_at=project.updated_at
        ))
    
    return RecentProjectsResponse(
        projects=recent_projects,
        total=len(recent_projects)
    )


@router.get("/recent-tasks", response_model=RecentTasksResponse)
async def get_recent_tasks(
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    limit: int = Query(5, ge=1, le=20, description="Number of tasks to return"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent tasks for the dashboard.
    """
    # Get or create user
    user = get_user_by_claims(current_user, db)
    
    # Check organization access
    if not check_org_membership(user.id, org_id, db):
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    # Get projects for this org
    projects = db.query(Project).filter(Project.org_id == org_id).all()
    project_ids = [p.id for p in projects]
    
    if not project_ids:
        return RecentTasksResponse(tasks=[], total=0)
    
    # Get recent tasks
    tasks = db.query(Task).filter(
        Task.project_id.in_(project_ids),
        Task.is_deleted == False
    ).order_by(Task.updated_at.desc()).limit(limit).all()
    
    # Build response
    recent_tasks = []
    priority_colors = {
        "urgent": "red",
        "high": "orange",
        "medium": "yellow",
        "low": "green"
    }
    
    for task in tasks:
        project = next((p for p in projects if p.id == task.project_id), None)
        today = date.today()
        
        recent_tasks.append(RecentTaskRow(
            id=task.id,
            title=task.title,
            project_id=task.project_id,
            project_title=project.title if project else "Unknown",
            priority=task.priority,
            priority_color=priority_colors.get(task.priority, "gray"),
            status=task.status,
            due_date=task.due_date,
            is_overdue=task.due_date and task.due_date < today and task.status != "completed",
            assigned_to_name=None,
            assigned_to_avatar=None
        ))
    
    return RecentTasksResponse(
        tasks=recent_tasks,
        total=len(recent_tasks)
    )