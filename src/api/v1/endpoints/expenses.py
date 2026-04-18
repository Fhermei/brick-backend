"""
Expenses API Endpoints - Submit, approve, reject expenses
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from src.core.security import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.models.organization import OrgMember
from src.models.project import Project
from src.models.task import Task
from src.models.expense import Expense, ExpenseStatus, PaymentMethod, ExpenseCategory
from src.schemas.expense import ExpenseCreate, ExpenseApprove, ExpenseReject, ExpenseResponse, ExpenseListResponse
from src.services.notification_service import notification_service
from src.services.audit_service import audit_service
from src.core.kpi import compute_bur, get_bur_status

router = APIRouter()


def check_org_access(user_id: uuid.UUID, org_id: uuid.UUID, db: Session) -> bool:
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id,
        OrgMember.status == "active"
    ).first()
    return membership is not None


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    task_id: uuid.UUID = Query(..., description="Task ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an expense for a task - automatically approved and updates task budget"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get task
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get project
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    if not check_org_access(user.id, project.org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Calculate new total spent
    current_spent = float(task.total_spent or 0)
    new_amount = float(expense_data.amount)
    new_total_spent = current_spent + new_amount
    
    # Check if expense exceeds task budget
    if new_total_spent > float(task.budget_allocated):
        raise HTTPException(
            status_code=400,
            detail=f"Expense would exceed task budget. Task budget: {task.budget_allocated}, Current spent: {current_spent}, Adding: {new_amount}"
        )
    
    # Create expense - AUTO APPROVED
    expense = Expense(
        task_id=task_id,
        user_id=user.id,
        amount=new_amount,
        payment_method=expense_data.payment_method,
        category=expense_data.category,
        receipt_url=expense_data.receipt_url,
        description=expense_data.description,
        status=ExpenseStatus.APPROVED,
        approved_by=user.id,
        approved_at=datetime.utcnow()
    )
    
    db.add(expense)
    db.flush()
    
    # CRITICAL: Update task total_spent
    task.total_spent = new_total_spent
    task.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(expense)
    db.refresh(task)
    
    print(f"Expense added: {new_amount} to task {task.id}. New total spent: {task.total_spent}")
    
    # Create audit log
    audit_service.log_action(
        db=db,
        org_id=project.org_id,
        user_id=user.id,
        action="create",
        entity_type="expense",
        entity_id=expense.id,
        new_values={"amount": new_amount, "task_id": str(task_id), "status": "approved", "new_task_total": float(task.total_spent)}
    )
    
    # Build response
    return ExpenseResponse(
        id=expense.id,
        task_id=task.id,
        task_title=task.title,
        project_id=project.id,
        project_title=project.title,
        user_id=user.id,
        user_name=user.name,
        amount=new_amount,
        payment_method=expense.payment_method.value,
        category=expense.category.value,
        receipt_url=expense.receipt_url,
        description=expense.description,
        status=expense.status.value,
        rejection_reason=expense.rejection_reason,
        approved_by=expense.approved_by,
        approved_by_name=user.name,
        approved_at=expense.approved_at,
        created_at=expense.created_at
    )

@router.get("/", response_model=ExpenseListResponse)
async def list_expenses(
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    status_filter: Optional[str] = Query(None, description="pending, approved, rejected"),
    task_id: Optional[uuid.UUID] = Query(None, description="Filter by task"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List expenses with filters - fixed to properly join with organization"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check access
    if not check_org_access(user.id, org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Build query - properly join through Task to Project to Organization
    query = db.query(Expense).join(Task, Expense.task_id == Task.id).join(Project, Task.project_id == Project.id).filter(Project.org_id == org_id)
    
    if status_filter:
        query = query.filter(Expense.status == status_filter)
    
    if task_id:
        query = query.filter(Expense.task_id == task_id)
    
    total = query.count()
    expenses = query.order_by(Expense.created_at.desc()).offset(offset).limit(limit).all()
    
    print(f"Found {total} expenses for organization {org_id}")
    
    # Build responses
    expense_responses = []
    for expense in expenses:
        task = db.query(Task).filter(Task.id == expense.task_id).first()
        project = db.query(Project).filter(Project.id == task.project_id).first() if task else None
        submitter = db.query(User).filter(User.id == expense.user_id).first()
        approver = db.query(User).filter(User.id == expense.approved_by).first() if expense.approved_by else None
        
        expense_responses.append(ExpenseResponse(
            id=expense.id,
            task_id=expense.task_id,
            task_title=task.title if task else "Unknown",
            project_id=project.id if project else None,
            project_title=project.title if project else "Unknown",
            user_id=expense.user_id,
            user_name=submitter.name if submitter else "Unknown",
            amount=float(expense.amount),
            payment_method=expense.payment_method.value,
            category=expense.category.value,
            receipt_url=expense.receipt_url,
            description=expense.description,
            status=expense.status.value,
            rejection_reason=expense.rejection_reason,
            approved_by=expense.approved_by,
            approved_by_name=approver.name if approver else None,
            approved_at=expense.approved_at,
            created_at=expense.created_at
        ))
    
    return ExpenseListResponse(total=total, expenses=expense_responses)

@router.get("/task/{task_id}", response_model=ExpenseListResponse)
async def get_task_expenses(
    task_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all expenses for a specific task"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get project
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    if not check_org_access(user.id, project.org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get expenses for this task
    expenses = db.query(Expense).filter(Expense.task_id == task_id).order_by(Expense.created_at.desc()).all()
    
    expense_responses = []
    for expense in expenses:
        submitter = db.query(User).filter(User.id == expense.user_id).first()
        approver = db.query(User).filter(User.id == expense.approved_by).first() if expense.approved_by else None
        
        expense_responses.append(ExpenseResponse(
            id=expense.id,
            task_id=expense.task_id,
            task_title=task.title,
            project_id=project.id,
            project_title=project.title,
            user_id=expense.user_id,
            user_name=submitter.name if submitter else "Unknown",
            amount=float(expense.amount),
            payment_method=expense.payment_method.value,
            category=expense.category.value,
            receipt_url=expense.receipt_url,
            description=expense.description,
            status=expense.status.value,
            rejection_reason=expense.rejection_reason,
            approved_by=expense.approved_by,
            approved_by_name=approver.name if approver else None,
            approved_at=expense.approved_at,
            created_at=expense.created_at
        ))
    
    return ExpenseListResponse(total=len(expense_responses), expenses=expense_responses)