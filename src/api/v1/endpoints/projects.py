"""
Projects API Endpoints

CRUD operations for projects including:
- Create project with automatic owner assignment
- List projects with filtering
- Get single project with KPI calculations
- Update project
- Delete (soft delete) project
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import date, datetime
import uuid

from src.core.security import get_current_user
from src.core.kpi import (
    compute_bur, get_bur_status, compute_bbr, compute_days_to_exhaust,
    get_kar_status, calculate_days_elapsed, calculate_remaining_days
)
from src.db.session import get_db
from src.models.user import User
from src.models.organization import Organization, OrgMember
from src.models.project import Project
from src.models.project import Project, ProjectMember
from src.models.task import Task
from src.models.expense import Expense
from src.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse

router = APIRouter()


def check_org_access(user_id: uuid.UUID, org_id: uuid.UUID, db: Session) -> bool:
    """Check if user has access to the organization"""
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id,
        OrgMember.status == "active"
    ).first()
    return membership is not None


def get_user_role_in_org(user_id: uuid.UUID, org_id: uuid.UUID, db: Session) -> str:
    """Get user's role in the organization"""
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id,
        OrgMember.status == "active"
    ).first()
    return membership.role if membership else None


async def get_project_response(project_id: uuid.UUID, db: Session) -> ProjectResponse:
    """Get project with all KPI calculations"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all tasks for this project
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    # Get all approved expenses for tasks in this project
    task_ids = [t.id for t in tasks]
    expenses = []
    if task_ids:
        expenses = db.query(Expense).filter(
            Expense.task_id.in_(task_ids),
            Expense.status == "approved"
        ).all()
    
    # Calculate budget metrics
    total_spent = sum(e.amount for e in expenses)
    bur = compute_bur(total_spent, project.total_budget)
    bur_info = get_bur_status(bur)
    
    # Calculate task metrics
    total_tasks = len(tasks)
    today = date.today()
    completed_tasks = sum(1 for t in tasks if t.status == "completed")
    overdue_tasks = sum(1 for t in tasks if t.due_date and t.due_date < today and t.status != "completed")
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate KAR (using task completion as KPI for now)
    kar = completion_rate
    kar_info = get_kar_status(kar)
    
    # Calculate time metrics
    days_elapsed = calculate_days_elapsed(project.start_date)
    days_remaining = calculate_remaining_days(project.end_date)
    
    # Calculate BBR
    bbr = compute_bbr(total_spent, days_elapsed) if days_elapsed > 0 else 0
    remaining_budget = project.total_budget - total_spent
    days_to_exhaust = compute_days_to_exhaust(remaining_budget, bbr) if bbr > 0 else 999
    
    # Get member count
    member_count = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).count()
    
    return ProjectResponse(
        id=project.id,
        org_id=project.org_id,
        title=project.title,
        description=project.description,
        emoji=project.emoji,
        image_url=project.image_url,
        status=project.status,
        start_date=project.start_date,
        end_date=project.end_date,
        total_budget=project.total_budget,
        currency=project.currency,
        created_by=project.created_by,
        created_at=project.created_at,
        updated_at=project.updated_at,
        total_spent=round(total_spent, 2),
        bur=bur,
        bur_status=bur_info["status"],
        bur_color=bur_info["color"],
        bur_alert=bur_info.get("alert"),
        kar=kar,
        kar_status=kar_info["status"],
        kar_color=kar_info["color"],
        bbr=round(bbr, 2),
        days_to_exhaust=days_to_exhaust,
        days_elapsed=days_elapsed,
        days_remaining=days_remaining,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks,
        completion_rate=round(completion_rate, 2),
        member_count=member_count
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project within an organization.
    """
    # Get user from database - FIXED with fallback
    email = current_user.get("email") or current_user.get("username")
    cognito_sub = current_user.get("sub")
    
    print(f"Create project - Email: {email}, Cognito Sub: {cognito_sub}", flush=True)
    
    # Try to find user by cognito_sub first
    user = None
    if cognito_sub:
        user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
    
    # If not found, try by email
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
    
    # If still not found, create the user
    if not user:
        print(f"User not found, creating fallback user for email: {email}", flush=True)
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
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found and could not be created")
    
    # Check organization access
    if not check_org_access(user.id, org_id, db):
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    # Rest of the function remains the same...
    # Check if organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Create project
    project = Project(
        org_id=org_id,
        title=project_data.title,
        description=project_data.description,
        emoji=project_data.emoji,
        image_url=project_data.image_url,
        status=project_data.status,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        total_budget=project_data.total_budget,
        currency=project_data.currency,
        created_by=user.id
    )
    
    db.add(project)
    db.flush()
    
    # Add creator as project owner
    project_member = ProjectMember(
        project_id=project.id,
        user_id=user.id,
        role_id="owner"
    )
    db.add(project_member)
    
    db.commit()
    db.refresh(project)
    
    # Return project with KPI calculations
    return await get_project_response(project.id, db)


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by title"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all projects in an organization with optional filtering.
    """
    # Get user from database - FIXED with fallback
    email = current_user.get("email") or current_user.get("username")
    cognito_sub = current_user.get("sub")
    
    print(f"List projects - Email: {email}, Cognito Sub: {cognito_sub}", flush=True)
    
    # Try to find user by cognito_sub first
    user = None
    if cognito_sub:
        user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
    
    # If not found, try by email
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
    
    # If still not found, create the user
    if not user:
        print(f"User not found, creating fallback user for email: {email}", flush=True)
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
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found and could not be created")
    
    # Check organization access
    if not check_org_access(user.id, org_id, db):
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    # Rest of the function remains the same...
    # Build query
    query = db.query(Project).filter(Project.org_id == org_id)
    
    if status_filter:
        query = query.filter(Project.status == status_filter)
    
    if search:
        query = query.filter(Project.title.ilike(f"%{search}%"))
    
    # Get total count
    total = query.count()
    
    # Get projects with pagination
    projects = query.order_by(Project.updated_at.desc()).offset(offset).limit(limit).all()
    
    # Get responses with KPI calculations
    project_responses = []
    for project in projects:
        project_responses.append(await get_project_response(project.id, db))
    
    return ProjectListResponse(
        total=total,
        projects=project_responses
    )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single project by ID with full KPI calculations.
    """
    # Get user from database - FIXED with fallback
    email = current_user.get("email") or current_user.get("username")
    cognito_sub = current_user.get("sub")
    
    # Try to find user by cognito_sub first
    user = None
    if cognito_sub:
        user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
    
    # If not found, try by email
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
    
    # If still not found, create the user
    if not user:
        print(f"User not found, creating fallback user for email: {email}", flush=True)
        user = User(
            name=email.split('@')[0] if email else "Unknown",
            email=email if email else f"{cognito_sub}@temp.com",
            cognito_sub=cognito_sub,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found and could not be created")
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to the organization
    if not check_org_access(user.id, project.org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return await get_project_response(project_id, db)

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a project. Only owner and admins can update.
    """
    # Get user from database - FIXED with fallback
    email = current_user.get("email") or current_user.get("username")
    cognito_sub = current_user.get("sub")
    
    # Try to find user by cognito_sub first
    user = None
    if cognito_sub:
        user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
    
    # If not found, try by email
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
    
    # If still not found, create the user
    if not user:
        print(f"User not found, creating fallback user for email: {email}", flush=True)
        user = User(
            name=email.split('@')[0] if email else "Unknown",
            email=email if email else f"{cognito_sub}@temp.com",
            cognito_sub=cognito_sub,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found and could not be created")
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission (owner or admin)
    org_role = get_user_role_in_org(user.id, project.org_id, db)
    if org_role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions. Only owners and admins can update projects.")
    
    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    
    return await get_project_response(project_id, db)

@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a project. Only owners can delete projects.
    """
    # Get user from database - FIXED with fallback
    email = current_user.get("email") or current_user.get("username")
    cognito_sub = current_user.get("sub")
    
    # Try to find user by cognito_sub first
    user = None
    if cognito_sub:
        user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
    
    # If not found, try by email
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
    
    # If still not found, create the user
    if not user:
        print(f"User not found, creating fallback user for email: {email}", flush=True)
        user = User(
            name=email.split('@')[0] if email else "Unknown",
            email=email if email else f"{cognito_sub}@temp.com",
            cognito_sub=cognito_sub,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found and could not be created")
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is the owner of the organization
    org = db.query(Organization).filter(Organization.id == project.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if org.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only organization owners can delete projects")
    
    # Soft delete - set status to archived
    project.status = "archived"
    project.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": f"Project '{project.title}' has been archived successfully",
        "project_id": str(project_id)
    }

@router.post("/{project_id}/members/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str = Query("member", description="Role in the project"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a member to a project. Only project owners and admins can add members.
    
    **Path Parameters:**
    - `project_id`: UUID of the project
    - `user_id`: UUID of the user to add
    
    **Query Parameters:**
    - `role`: Role in the project (owner, admin, member, viewer)
    """
    # Get current user
    email = current_user.get("email") or current_user.get("username")
    current_user_obj = db.query(User).filter(User.email == email).first()
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permission
    org_role = get_user_role_in_org(current_user_obj.id, project.org_id, db)
    if org_role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if user exists
    user_to_add = db.query(User).filter(User.id == user_id).first()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this project")
    
    # Add member
    project_member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role_id=role
    )
    db.add(project_member)
    db.commit()
    
    return {
        "message": f"User {user_to_add.name} added to project {project.title}",
        "project_id": str(project_id),
        "user_id": str(user_id),
        "role": role
    }


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_200_OK)
async def remove_project_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from a project.
    
    **Path Parameters:**
    - `project_id`: UUID of the project
    - `user_id`: UUID of the user to remove
    """
    # Get current user
    email = current_user.get("email") or current_user.get("username")
    current_user_obj = db.query(User).filter(User.email == email).first()
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permission
    org_role = get_user_role_in_org(current_user_obj.id, project.org_id, db)
    if org_role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Cannot remove the project owner
    if user_id == project.created_by:
        raise HTTPException(status_code=400, detail="Cannot remove the project owner")
    
    # Remove member
    project_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    
    if not project_member:
        raise HTTPException(status_code=404, detail="Member not found in this project")
    
    db.delete(project_member)
    db.commit()
    
    return {
        "message": "Member removed from project successfully",
        "project_id": str(project_id),
        "user_id": str(user_id)
    }
    
    
@router.get("/{project_id}/members-for-assignment")
async def get_project_members_for_assignment(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all organization members that can be assigned to tasks in this project"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all organization members
    org_members = db.query(OrgMember).filter(
        OrgMember.org_id == project.org_id,
        OrgMember.status == "active"
    ).all()
    
    members = []
    for m in org_members:
        user_obj = db.query(User).filter(User.id == m.user_id).first()
        if user_obj:
            members.append({
                "id": str(user_obj.id),
                "name": user_obj.name,
                "email": user_obj.email,
                "role": m.role
            })
    
    return {"members": members}