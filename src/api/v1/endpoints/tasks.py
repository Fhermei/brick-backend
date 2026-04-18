"""
Tasks API Endpoints - Complete CRUD with subtasks, budget tracking, multi-assignee
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime, date
import uuid

from src.core.security import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.models.organization import OrgMember
from src.models.project import Project, ProjectMember
from src.models.task import Task, TaskAssignee, TaskBudgetItem
from src.models.expense import Expense
from src.schemas.task import (
    TaskCreate, TaskUpdate, TaskStatusUpdate,
    TaskResponse, TaskListResponse, TaskAssigneeResponse,
    TaskBudgetItemCreate, TaskBudgetItemResponse
)
from src.services.notification_service import notification_service

router = APIRouter()


def check_org_access(user_id: uuid.UUID, org_id: uuid.UUID, db: Session) -> bool:
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id,
        OrgMember.status == "active"
    ).first()
    return membership is not None


def get_user_role_in_org(user_id: uuid.UUID, org_id: uuid.UUID, db: Session) -> str:
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id,
        OrgMember.status == "active"
    ).first()
    return membership.role if membership else None


def get_project_role(user_id: uuid.UUID, project_id: uuid.UUID, db: Session) -> str:
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    return member.role_id if member else None


def get_task_assignee_ids(task_id: uuid.UUID, db: Session) -> List[uuid.UUID]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return []
    
    assignee_ids = []
    if task.assigned_to:
        assignee_ids.append(task.assigned_to)
    
    additional = db.query(TaskAssignee.user_id).filter(TaskAssignee.task_id == task_id).all()
    assignee_ids.extend([a[0] for a in additional])
    
    return list(set(assignee_ids))


def get_project_members_for_task(project_id: uuid.UUID, db: Session) -> List[dict]:
    """Get all project members for task assignment"""
    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    result = []
    for m in members:
        user_obj = db.query(User).filter(User.id == m.user_id).first()
        if user_obj:
            result.append({
                "id": str(user_obj.id),
                "name": user_obj.name,
                "email": user_obj.email,
                "role": m.role_id
            })
    return result


def get_task_response(task_id: uuid.UUID, db: Session) -> TaskResponse:
    """Get complete task response with all relationships"""
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    
    # Get parent task info
    parent_task = None
    parent_task_title = None
    if task.parent_task_id:
        parent_task = db.query(Task).filter(Task.id == task.parent_task_id).first()
        parent_task_title = parent_task.title if parent_task else None
    
    # Get primary assignee info
    assignee_name = None
    if task.assigned_to:
        assignee = db.query(User).filter(User.id == task.assigned_to).first()
        assignee_name = assignee.name if assignee else None
    
    # Get creator info
    creator = db.query(User).filter(User.id == task.created_by).first()
    creator_name = creator.name if creator else "Unknown"
    
    # Get additional assignees
    additional = db.query(TaskAssignee).filter(TaskAssignee.task_id == task_id).all()
    additional_assignees = []
    for a in additional:
        user = db.query(User).filter(User.id == a.user_id).first()
        if user:
            additional_assignees.append(TaskAssigneeResponse(
                id=a.id,
                user_id=a.user_id,
                name=user.name,
                email=user.email,
                is_supervisor=a.is_supervisor,
                assigned_at=a.assigned_at
            ))
    
    # Get budget items
    budget_items = db.query(TaskBudgetItem).filter(TaskBudgetItem.task_id == task_id).all()
    budget_items_response = []
    for bi in budget_items:
        user = db.query(User).filter(User.id == bi.user_id).first()
        budget_items_response.append(TaskBudgetItemResponse(
            id=bi.id,
            amount=float(bi.amount),
            category=bi.category,
            description=bi.description,
            receipt_url=bi.receipt_url,
            is_approved=bi.is_approved,
            user_name=user.name if user else "Unknown",
            created_at=bi.created_at
        ))
    
    # Calculate total spent
    total_spent = sum(float(bi.amount) for bi in budget_items if bi.is_approved)
    
    # Get subtasks
    subtasks = db.query(Task).filter(
        Task.parent_task_id == task_id,
        Task.is_deleted == False
    ).all()
    subtasks_response = [get_task_response(st.id, db) for st in subtasks]
    
    # Check if overdue
    is_overdue = task.due_date < date.today() and task.status != "completed"
    
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        project_title=project.title if project else "Unknown",
        parent_task_id=task.parent_task_id,
        parent_task_title=parent_task_title,
        title=task.title,
        description=task.description,
        type=task.type,
        priority=task.priority,
        status=task.status,
        assigned_to=task.assigned_to,
        assigned_to_name=assignee_name,
        date_assigned=task.date_assigned,
        due_date=task.due_date,
        completed_at=task.completed_at,
        budget_allocated=float(task.budget_allocated or 0),
        total_spent=total_spent,
        blocked_reason=task.blocked_reason,
        is_deleted=task.is_deleted,
        created_by=task.created_by,
        created_by_name=creator_name,
        created_at=task.created_at,
        updated_at=task.updated_at,
        additional_assignees=additional_assignees,
        subtasks=subtasks_response,
        budget_items=budget_items_response,
        custom_fields=task.custom_fields,
        is_overdue=is_overdue
    )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    project_id: uuid.UUID = Query(..., description="Project ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task within a project with multi-assignee support"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not check_org_access(user.id, project.org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if parent task exists
    if task_data.parent_task_id:
        parent = db.query(Task).filter(Task.id == task_data.parent_task_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent task not found")
    
    # Create task
    task = Task(
        project_id=project_id,
        parent_task_id=task_data.parent_task_id,
        title=task_data.title,
        description=task_data.description,
        type=task_data.type,
        priority=task_data.priority,
        status=task_data.status,
        assigned_to=task_data.assigned_to,
        due_date=task_data.due_date,
        budget_allocated=task_data.budget_allocated or 0,
        created_by=user.id,
        custom_fields=task_data.custom_fields
    )
    
    db.add(task)
    db.flush()
    
    # Add additional assignees
    for assignee_id in task_data.additional_assignees:
        task_assignee = TaskAssignee(
            task_id=task.id,
            user_id=assignee_id,
            is_supervisor=False
        )
        db.add(task_assignee)
    
    # Add supervisors
    for supervisor_id in task_data.supervisors:
        task_supervisor = TaskAssignee(
            task_id=task.id,
            user_id=supervisor_id,
            is_supervisor=True
        )
        db.add(task_supervisor)
    
    db.commit()
    db.refresh(task)
    
    # Create activity log
    try:
        notification_service.create_activity(
            db=db,
            user_id=user.id,
            org_id=project.org_id,
            project_id=project_id,
            task_id=task.id,
            action="task_created",
            description=f"Task '{task.title}' was created",
            extra_info={"task_title": task.title, "created_by": user.name}
        )
    except Exception as e:
        print(f"Activity log failed: {e}")
    
    return get_task_response(task.id, db)


@router.get("/", response_model=TaskListResponse)
def list_tasks(
    project_id: Optional[uuid.UUID] = Query(None, description="Filter by project ID"),
    org_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    priority_filter: Optional[str] = Query(None, description="Filter by priority"),
    assigned_to_me: bool = Query(False, description="Only tasks assigned to current user"),
    search: Optional[str] = Query(None, description="Search by title"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List tasks with various filters"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    query = db.query(Task).filter(Task.is_deleted == False)
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
        project = db.query(Project).filter(Project.id == project_id).first()
        if project and not check_org_access(user.id, project.org_id, db):
            raise HTTPException(status_code=403, detail="Access denied")
    
    if org_id:
        projects = db.query(Project.id).filter(Project.org_id == org_id).all()
        project_ids = [p[0] for p in projects]
        query = query.filter(Task.project_id.in_(project_ids))
        if not check_org_access(user.id, org_id, db):
            raise HTTPException(status_code=403, detail="Access denied")
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    if priority_filter:
        query = query.filter(Task.priority == priority_filter)
    
    if assigned_to_me:
        primary_condition = Task.assigned_to == user.id
        additional_condition = Task.id.in_(
            db.query(TaskAssignee.task_id).filter(TaskAssignee.user_id == user.id)
        )
        query = query.filter(or_(primary_condition, additional_condition))
    
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))
    
    total = query.count()
    tasks = query.order_by(Task.due_date.asc()).offset(offset).limit(limit).all()
    
    task_responses = []
    for task in tasks:
        task_responses.append(get_task_response(task.id, db))
    
    return TaskListResponse(total=total, tasks=task_responses)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single task by ID"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not check_org_access(user.id, project.org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return get_task_response(task_id, db)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    
    # Check permissions
    org_role = get_user_role_in_org(user.id, project.org_id, db)
    project_role = get_project_role(user.id, task.project_id, db)
    is_assignee = task.assigned_to == user.id
    
    can_edit = (org_role in ["owner", "admin", "manager"] or 
                project_role in ["owner", "admin"] or
                is_assignee)
    
    if not can_edit:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "additional_assignees" and value is not None:
            # Update additional assignees
            existing = db.query(TaskAssignee).filter(TaskAssignee.task_id == task_id).all()
            existing_ids = [a.user_id for a in existing]
            
            # Add new ones
            for assignee_id in value:
                if assignee_id not in existing_ids and assignee_id != task.assigned_to:
                    new_assignee = TaskAssignee(task_id=task_id, user_id=assignee_id, is_supervisor=False)
                    db.add(new_assignee)
            
            # Remove old ones not in list
            for assignee in existing:
                if assignee.user_id not in value and assignee.user_id != task.assigned_to:
                    db.delete(assignee)
        elif field == "assigned_to":
            task.assigned_to = value
        elif field != "additional_assignees" and field != "supervisors":
            setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return get_task_response(task_id, db)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: uuid.UUID,
    status_data: TaskStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task status - allows moving between any status"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    
    # Check permissions - allow assignees and project members
    org_role = get_user_role_in_org(user.id, project.org_id, db)
    project_role = get_project_role(user.id, task.project_id, db)
    is_assignee = task.assigned_to == user.id
    is_additional_assignee = db.query(TaskAssignee).filter(
        TaskAssignee.task_id == task_id,
        TaskAssignee.user_id == user.id
    ).first() is not None
    
    can_update = (org_role in ["owner", "admin", "manager"] or 
                  project_role in ["owner", "admin"] or
                  is_assignee or is_additional_assignee)
    
    if not can_update:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update task status")
    
    old_status = task.status
    new_status = status_data.status
    
    # Allow any status change, just prevent completed tasks from changing
    if old_status == "completed" and new_status != "completed":
        raise HTTPException(status_code=400, detail="Cannot change status of a completed task")
    
    task.status = new_status
    
    if new_status == "blocked":
        task.blocked_reason = status_data.blocked_reason or "No reason provided"
    else:
        task.blocked_reason = None
    
    if new_status == "completed":
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    # Create activity log
    try:
        notification_service.create_activity(
            db=db,
            user_id=user.id,
            org_id=project.org_id,
            project_id=project.id,
            task_id=task.id,
            action="task_status_changed",
            description=f"Task '{task.title}' status changed from {old_status} to {new_status}",
            extra_info={"old_status": old_status, "new_status": new_status, "changed_by": user.name}
        )
    except Exception as e:
        print(f"Activity log failed: {e}")
    
    return get_task_response(task_id, db)


@router.post("/{task_id}/budget", response_model=TaskBudgetItemResponse, status_code=status.HTTP_201_CREATED)
def add_budget_item(
    task_id: uuid.UUID,
    budget_data: TaskBudgetItemCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a budget item to a task (expense tracking)"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    
    # Check if user has access
    if not check_org_access(user.id, project.org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if adding this would exceed budget
    current_spent = sum(float(bi.amount) for bi in db.query(TaskBudgetItem).filter(
        TaskBudgetItem.task_id == task_id,
        TaskBudgetItem.is_approved == True
    ).all())
    
    new_total = current_spent + budget_data.amount
    if new_total > float(task.budget_allocated):
        raise HTTPException(
            status_code=400, 
            detail=f"Budget exceeded! Allocated: {task.budget_allocated}, Spent: {current_spent}, Adding: {budget_data.amount}"
        )
    
    budget_item = TaskBudgetItem(
        task_id=task_id,
        user_id=user.id,
        amount=budget_data.amount,
        category=budget_data.category,
        description=budget_data.description,
        receipt_url=budget_data.receipt_url,
        is_approved=True,  # Auto-approve for now
        approved_by=user.id,
        approved_at=datetime.utcnow()
    )
    
    db.add(budget_item)
    db.commit()
    db.refresh(budget_item)
    
    # Update task total spent
    task.total_spent = float(task.total_spent or 0) + budget_data.amount
    db.commit()
    
    return TaskBudgetItemResponse(
        id=budget_item.id,
        amount=float(budget_item.amount),
        category=budget_item.category,
        description=budget_item.description,
        receipt_url=budget_item.receipt_url,
        is_approved=budget_item.is_approved,
        user_name=user.name,
        created_at=budget_item.created_at
    )


@router.get("/{task_id}/members", response_model=List[dict])
def get_task_available_members(
    task_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all project members that can be assigned to this task"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return get_project_members_for_task(task.project_id, db)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: uuid.UUID,
    permanent: bool = Query(False, description="Permanently delete"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete or archive a task. Only admins/managers can delete permanently."""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = db.query(Project).filter(Project.id == task.project_id).first()
    
    # Check if user has admin/manager role for permanent deletion
    org_role = get_user_role_in_org(user.id, project.org_id, db)
    project_role = get_project_role(user.id, task.project_id, db)
    
    can_permanently_delete = (org_role in ["owner", "admin"] or project_role in ["owner", "admin"])
    
    if permanent:
        if not can_permanently_delete:
            raise HTTPException(status_code=403, detail="Only admins can permanently delete tasks")
        db.delete(task)
        db.commit()
        return {"message": f"Task '{task.title}' permanently deleted", "task_id": str(task_id)}
    else:
        # Soft delete - archive
        if not (can_permanently_delete or task.created_by == user.id):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        task.is_deleted = True
        task.updated_at = datetime.utcnow()
        db.commit()
        return {"message": f"Task '{task.title}' archived", "task_id": str(task_id)}