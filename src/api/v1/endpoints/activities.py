"""
Activities API Endpoints - Get recent activities for dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from src.core.security import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.models.organization import OrgMember
from src.models.activity_log import ActivityLog

router = APIRouter()


@router.get("/recent")
async def get_recent_activities(
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    limit: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent activities for the organization dashboard"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check organization access
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user.id,
        OrgMember.status == "active"
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get recent activities
    activities = db.query(ActivityLog).filter(
        ActivityLog.org_id == org_id
    ).order_by(ActivityLog.created_at.desc()).limit(limit).all()
    
    # Build response with user details
    result = []
    for activity in activities:
        user_obj = db.query(User).filter(User.id == activity.user_id).first()
        result.append({
            "id": str(activity.id),
            "user_name": user_obj.name if user_obj else "Unknown",
            "user_avatar": user_obj.name[0] if user_obj else "U",
            "action": activity.action,
            "description": activity.description,
            "created_at": activity.created_at.isoformat(),
            "extra_info": activity.extra_info
        })
    
    return {"activities": result, "total": len(result)}