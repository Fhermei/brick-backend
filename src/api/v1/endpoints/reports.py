"""
Reports API Endpoints - Generate and download PDF reports
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from src.core.security import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.models.organization import Organization, OrgMember
from src.models.project import Project
from src.models.task import Task, TaskAssignee
from src.models.expense import Expense
from src.models.kpi import KPI
from src.schemas.report import ReportGenerateRequest
from src.services.report_service import report_service
from src.services.audit_service import audit_service

router = APIRouter()


def check_org_access(user_id: uuid.UUID, org_id: uuid.UUID, db: Session) -> bool:
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id,
        OrgMember.status == "active"
    ).first()
    return membership is not None


@router.post("/generate")
async def generate_report(
    report_request: ReportGenerateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a PDF report for organization or project"""
    try:
        user_id = current_user.get("id")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Check organization access
        if not check_org_access(user.id, report_request.org_id, db):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get organization
        org = db.query(Organization).filter(Organization.id == report_request.org_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Validate report type
        if report_request.type not in ["organization", "project"]:
            raise HTTPException(status_code=400, detail=f"Invalid report type: {report_request.type}")
        
        if report_request.type == "project" and not report_request.project_id:
            raise HTTPException(status_code=400, detail="Project ID is required for project report")
        
        # Get data based on report type
        projects_data = []
        tasks_data = []
        expenses_data = []
        kpis_data = []
        
        if report_request.type == "organization":
            # Get all projects
            projects = db.query(Project).filter(
                Project.org_id == report_request.org_id,
                Project.status != "archived"
            ).all()
            
            for p in projects:
                # Get task IDs for this project
                project_task_ids = [t.id for t in db.query(Task.id).filter(Task.project_id == p.id).all()]
                
                # Get approved expenses for this project
                project_expenses = []
                if project_task_ids:
                    project_expenses = db.query(Expense).filter(
                        Expense.task_id.in_(project_task_ids),
                        Expense.status == "approved"
                    ).all()
                total_spent = sum(float(e.amount) for e in project_expenses)
                
                # Get task count
                task_count = db.query(Task).filter(
                    Task.project_id == p.id,
                    Task.is_deleted == False
                ).count()
                
                projects_data.append({
                    "id": str(p.id),
                    "title": p.title,
                    "total_budget": float(p.total_budget),
                    "total_spent": total_spent,
                    "status": p.status,
                    "start_date": p.start_date.isoformat() if p.start_date else None,
                    "end_date": p.end_date.isoformat() if p.end_date else None,
                    "task_count": task_count
                })
            
            # Get all tasks with additional details
            tasks = db.query(Task).join(Project).filter(
                Project.org_id == report_request.org_id, 
                Task.is_deleted == False
            ).all()
            
            for t in tasks:
                # Get additional assignees
                additional_assignees = db.query(TaskAssignee).filter(
                    TaskAssignee.task_id == t.id
            ).all()
                
                # Check if overdue
                is_overdue = t.due_date and t.due_date < datetime.utcnow().date() and t.status != "completed"
                
                # Get payment method from expenses
                payment_method = None
                task_expenses = db.query(Expense).filter(
                    Expense.task_id == t.id,
                    Expense.status == "approved"
                ).first()
                if task_expenses:
                    payment_method = task_expenses.payment_method.value if task_expenses.payment_method else None
                
                tasks_data.append({
                    "id": str(t.id),
                    "project_id": str(t.project_id),
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "assigned_to_name": t.assigned_to_user.name if t.assigned_to else None,
                    "additional_assignees_count": len(additional_assignees),
                    "budget_allocated": float(t.budget_allocated or 0),
                    "total_spent": float(t.total_spent or 0),
                    "is_overdue": is_overdue,
                    "payment_method": payment_method,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                })
            
            # Get all approved expenses
            expenses = db.query(Expense).join(Task).join(Project).filter(
                Expense.status == "approved",
                Project.org_id == report_request.org_id
            ).all()
            
            for e in expenses:
                task = db.query(Task).filter(Task.id == e.task_id).first()
                project = db.query(Project).filter(Project.id == task.project_id).first() if task else None
                submitter = db.query(User).filter(User.id == e.user_id).first()
                
                expenses_data.append({
                    "id": str(e.id),
                    "task_id": str(e.task_id),
                    "task_title": task.title if task else "Unknown",
                    "project_id": str(task.project_id) if task else None,
                    "project_title": project.title if project else "Unknown",
                    "amount": float(e.amount),
                    "category": e.category.value,
                    "payment_method": e.payment_method.value,
                    "user_name": submitter.name if submitter else "Unknown",
                    "status": e.status.value,
                    "created_at": e.created_at.isoformat() if e.created_at else None
                })
            
            # Get KPIs
            kpis = db.query(KPI).join(Project).filter(Project.org_id == report_request.org_id).all()
            for k in kpis:
                project = db.query(Project).filter(Project.id == k.project_id).first()
                kpis_data.append({
                    "id": str(k.id),
                    "project_id": str(k.project_id),
                    "project_title": project.title if project else "Unknown",
                    "indicator_name": k.indicator_name,
                    "description": k.description,
                    "target_value": float(k.target_value),
                    "actual_value": float(k.actual_value) if k.actual_value else None,
                    "kar": float(k.kar) if k.kar else None,
                    "status": k.status,
                    "unit": k.unit,
                    "period_start": k.period_start.isoformat() if k.period_start else None,
                    "period_end": k.period_end.isoformat() if k.period_end else None
                })
        
        elif report_request.type == "project" and report_request.project_id:
            project = db.query(Project).filter(Project.id == report_request.project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Get approved expenses for this project
            project_task_ids = [t.id for t in db.query(Task.id).filter(Task.project_id == project.id).all()]
            project_expenses = []
            if project_task_ids:
                project_expenses = db.query(Expense).filter(
                    Expense.task_id.in_(project_task_ids),
                    Expense.status == "approved"
                ).all()
            total_spent = sum(float(e.amount) for e in project_expenses)
            
            projects_data = [{
                "id": str(project.id),
                "title": project.title,
                "total_budget": float(project.total_budget),
                "total_spent": total_spent,
                "status": project.status,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "end_date": project.end_date.isoformat() if project.end_date else None
            }]
            
            # Get tasks with all details
            tasks = db.query(Task).filter(
                Task.project_id == report_request.project_id,
                Task.is_deleted == False
            ).all()
            
            for t in tasks:
                # Get additional assignees
                additional_assignees = db.query(TaskAssignee).filter(
                    TaskAssignee.task_id == t.id
                ).all()
                
                # Check if overdue
                is_overdue = t.due_date and t.due_date < datetime.utcnow().date() and t.status != "completed"
                
                # Get payment method from expenses
                payment_method = None
                task_expenses = db.query(Expense).filter(
                    Expense.task_id == t.id,
                    Expense.status == "approved"
                ).first()
                if task_expenses:
                    payment_method = task_expenses.payment_method.value if task_expenses.payment_method else None
                
                tasks_data.append({
                    "id": str(t.id),
                    "project_id": str(t.project_id),
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "assigned_to_name": t.assigned_to_user.name if t.assigned_to else None,
                    "additional_assignees_count": len(additional_assignees),
                    "budget_allocated": float(t.budget_allocated or 0),
                    "total_spent": float(t.total_spent or 0),
                    "is_overdue": is_overdue,
                    "payment_method": payment_method,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                })
            
            # Get expenses for this project
            expenses = db.query(Expense).join(Task).filter(
                Expense.status == "approved",
                Task.project_id == report_request.project_id
            ).all()
            
            for e in expenses:
                task = db.query(Task).filter(Task.id == e.task_id).first()
                submitter = db.query(User).filter(User.id == e.user_id).first()
                
                expenses_data.append({
                    "id": str(e.id),
                    "task_id": str(e.task_id),
                    "task_title": task.title if task else "Unknown",
                    "amount": float(e.amount),
                    "category": e.category.value,
                    "payment_method": e.payment_method.value,
                    "user_name": submitter.name if submitter else "Unknown",
                    "status": e.status.value,
                    "created_at": e.created_at.isoformat() if e.created_at else None
                })
            
            # Get KPIs for this project
            kpis = db.query(KPI).filter(KPI.project_id == report_request.project_id).all()
            for k in kpis:
                kpis_data.append({
                    "id": str(k.id),
                    "project_id": str(k.project_id),
                    "project_title": project.title,
                    "indicator_name": k.indicator_name,
                    "description": k.description,
                    "target_value": float(k.target_value),
                    "actual_value": float(k.actual_value) if k.actual_value else None,
                    "kar": float(k.kar) if k.kar else None,
                    "status": k.status,
                    "unit": k.unit,
                    "period_start": k.period_start.isoformat() if k.period_start else None,
                    "period_end": k.period_end.isoformat() if k.period_end else None
                })
        
        # Generate PDF report
        pdf_bytes = report_service.generate_organization_report(
            db=db,
            org_id=report_request.org_id,
            org_name=org.name,
            currency=org.currency,
            projects_data=projects_data,
            tasks_data=tasks_data,
            expenses_data=expenses_data,
            kpis_data=kpis_data,
            date_from=report_request.date_from,
            date_to=report_request.date_to
        )
        
        # Create audit log
        audit_service.log_action(
            db=db,
            org_id=report_request.org_id,
            user_id=user.id,
            action="generate",
            entity_type="report",
            new_values={"type": report_request.type, "project_id": str(report_request.project_id) if report_request.project_id else None}
        )
        
        # Generate proper filename
        current_date = datetime.utcnow().strftime('%Y%m%d')
        if report_request.type == "project" and report_request.project_id:
            project = db.query(Project).filter(Project.id == report_request.project_id).first()
            safe_project_name = project.title.replace(' ', '_').replace('/', '_').replace('\\', '_')[:50]
            filename = f"Brick_SPMES_Project_Report_{safe_project_name}_{current_date}.pdf"
        else:
            safe_org_name = org.name.replace(' ', '_').replace('/', '_').replace('\\', '_')[:50]
            filename = f"Brick_SPMES_Org_Report_{safe_org_name}_{current_date}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")