"""
KPIs API Endpoints - Create and track KPIs for projects
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
from src.models.kpi import KPI
from src.schemas.kpi import KPICreate, KPIUpdate, KPIResponse, KPIListResponse
from src.services.kpi_service import kpi_service
from src.services.audit_service import audit_service

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


@router.post("/", response_model=KPIResponse, status_code=status.HTTP_201_CREATED)
async def create_kpi(
    kpi_data: KPICreate,
    project_id: uuid.UUID = Query(..., description="Project ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new KPI for a project (admin/manager only)"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permission
    user_role = get_user_role_in_org(user.id, project.org_id, db)
    if user_role not in ["owner", "admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only admins and managers can create KPIs")
    
    # Validate period
    if kpi_data.period_start > kpi_data.period_end:
        raise HTTPException(status_code=400, detail="Period start must be before period end")
    
    # Create KPI
    kpi = KPI(
        project_id=project_id,
        created_by=user.id,
        indicator_name=kpi_data.indicator_name,
        description=kpi_data.description,
        target_value=kpi_data.target_value,
        unit=kpi_data.unit,
        period_start=kpi_data.period_start,
        period_end=kpi_data.period_end
    )
    
    db.add(kpi)
    db.commit()
    db.refresh(kpi)
    
    # Create audit log
    audit_service.log_action(
        db=db,
        org_id=project.org_id,
        user_id=user.id,
        action="create",
        entity_type="kpi",
        entity_id=kpi.id,
        new_values={"indicator_name": kpi_data.indicator_name, "target_value": kpi_data.target_value}
    )
    
    return KPIResponse(
        id=kpi.id,
        project_id=kpi.project_id,
        project_title=project.title,
        indicator_name=kpi.indicator_name,
        description=kpi.description,
        target_value=float(kpi.target_value),
        actual_value=float(kpi.actual_value) if kpi.actual_value else None,
        kar=float(kpi.kar) if kpi.kar else None,
        status=kpi.status,
        unit=kpi.unit,
        period_start=kpi.period_start,
        period_end=kpi.period_end,
        created_by=kpi.created_by,
        created_by_name=user.name,
        created_at=kpi.created_at,
        updated_at=kpi.updated_at
    )


@router.get("/", response_model=KPIListResponse)
async def list_kpis(
    project_id: uuid.UUID = Query(..., description="Project ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all KPIs for a project"""
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
    
    # Get KPIs
    kpis = db.query(KPI).filter(KPI.project_id == project_id).order_by(KPI.created_at.desc()).all()
    
    kpi_responses = []
    for kpi in kpis:
        creator = db.query(User).filter(User.id == kpi.created_by).first()
        kpi_responses.append(KPIResponse(
            id=kpi.id,
            project_id=kpi.project_id,
            project_title=project.title,
            indicator_name=kpi.indicator_name,
            description=kpi.description,
            target_value=float(kpi.target_value),
            actual_value=float(kpi.actual_value) if kpi.actual_value else None,
            kar=float(kpi.kar) if kpi.kar else None,
            status=kpi.status,
            unit=kpi.unit,
            period_start=kpi.period_start,
            period_end=kpi.period_end,
            created_by=kpi.created_by,
            created_by_name=creator.name if creator else "Unknown",
            created_at=kpi.created_at,
            updated_at=kpi.updated_at
        ))
    
    return KPIListResponse(total=len(kpi_responses), kpis=kpi_responses)


@router.patch("/{kpi_id}", response_model=KPIResponse)
async def update_kpi_actual(
    kpi_id: uuid.UUID,
    kpi_data: KPIUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update actual value for a KPI (any project member can log)"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get KPI
    kpi = db.query(KPI).filter(KPI.id == kpi_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    
    # Get project
    project = db.query(Project).filter(Project.id == kpi.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    if not check_org_access(user.id, project.org_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update actual value
    kpi.actual_value = kpi_data.actual_value
    kpi.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(kpi)
    
    # Calculate KAR and check thresholds
    updated_kpi = kpi_service.calculate_and_update_kpi(db, kpi.id)
    if updated_kpi:
        kpi_service.check_kpi_thresholds(db, updated_kpi, project)
    
    # Create audit log
    audit_service.log_action(
        db=db,
        org_id=project.org_id,
        user_id=user.id,
        action="update",
        entity_type="kpi",
        entity_id=kpi.id,
        new_values={"actual_value": kpi_data.actual_value}
    )
    
    creator = db.query(User).filter(User.id == kpi.created_by).first()
    
    return KPIResponse(
        id=kpi.id,
        project_id=kpi.project_id,
        project_title=project.title,
        indicator_name=kpi.indicator_name,
        description=kpi.description,
        target_value=float(kpi.target_value),
        actual_value=float(kpi.actual_value) if kpi.actual_value else None,
        kar=float(kpi.kar) if kpi.kar else None,
        status=kpi.status,
        unit=kpi.unit,
        period_start=kpi.period_start,
        period_end=kpi.period_end,
        created_by=kpi.created_by,
        created_by_name=creator.name if creator else "Unknown",
        created_at=kpi.created_at,
        updated_at=kpi.updated_at
    )


@router.delete("/{kpi_id}", status_code=status.HTTP_200_OK)
async def delete_kpi(
    kpi_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a KPI (admin/manager only)"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get KPI
    kpi = db.query(KPI).filter(KPI.id == kpi_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    
    # Get project
    project = db.query(Project).filter(Project.id == kpi.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permission
    user_role = get_user_role_in_org(user.id, project.org_id, db)
    if user_role not in ["owner", "admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only admins and managers can delete KPIs")
    
    # Create audit log before deletion
    audit_service.log_action(
        db=db,
        org_id=project.org_id,
        user_id=user.id,
        action="delete",
        entity_type="kpi",
        entity_id=kpi.id,
        old_values={"indicator_name": kpi.indicator_name}
    )
    
    db.delete(kpi)
    db.commit()
    
    return {"message": "KPI deleted successfully", "kpi_id": str(kpi_id)}