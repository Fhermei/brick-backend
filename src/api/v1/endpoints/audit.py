"""
Audit API Endpoints - View audit logs (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from src.core.security import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.models.organization import OrgMember
from src.models.audit_log import AuditLog
from src.schemas.audit import AuditLogResponse, AuditLogListResponse

router = APIRouter()


def get_user_role_in_org(user_id: uuid.UUID, org_id: uuid.UUID, db: Session) -> str:
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user_id,
        OrgMember.status == "active"
    ).first()
    return membership.role if membership else None


@router.get("/", response_model=AuditLogListResponse)
async def get_audit_logs(
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    action: Optional[str] = Query(None, description="Filter by action"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs for an organization (admin/owner only)"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check if user has admin/owner role
    user_role = get_user_role_in_org(user.id, org_id, db)
    if user_role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owners and admins can view audit logs")
    
    # Build query
    query = db.query(AuditLog).filter(AuditLog.org_id == org_id)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    
    log_responses = []
    for log in logs:
        user_obj = db.query(User).filter(User.id == log.user_id).first()
        log_responses.append(AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_name=user_obj.name if user_obj else "Unknown",
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            old_values=log.old_values,
            new_values=log.new_values,
            created_at=log.created_at
        ))
    
    return AuditLogListResponse(total=total, logs=log_responses)