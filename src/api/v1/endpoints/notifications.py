"""
Notifications API Endpoints

List and manage user notifications.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from src.core.security import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.models.notification import Notification
from src.schemas.notification import NotificationResponse, NotificationListResponse, MarkReadRequest

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all notifications for the current user"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    query = db.query(Notification).filter(Notification.user_id == user.id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    total = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.is_read == False
    ).count()
    
    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    return NotificationListResponse(
        total=total,
        unread_count=unread_count,
        notifications=[
            NotificationResponse(
                id=n.id,
                type=n.type,
                title=n.title,
                message=n.message,
                data=n.data,
                is_read=n.is_read,
                created_at=n.created_at
            ) for n in notifications
        ]
    )


@router.patch("/mark-read", status_code=status.HTTP_200_OK)
async def mark_notifications_read(
    request: MarkReadRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notifications as read"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    db.query(Notification).filter(
        Notification.id.in_(request.notification_ids),
        Notification.user_id == user.id
    ).update({"is_read": True}, synchronize_session=False)
    
    db.commit()
    
    return {"message": f"{len(request.notification_ids)} notifications marked as read"}


@router.patch("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.is_read == False
    ).update({"is_read": True}, synchronize_session=False)
    
    db.commit()
    
    return {"message": "All notifications marked as read"}