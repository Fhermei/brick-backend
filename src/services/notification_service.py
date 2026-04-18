"""
Notification Service - Create and manage notifications
"""

from sqlalchemy.orm import Session
import uuid
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from src.models.notification import Notification
from src.models.activity_log import ActivityLog
from src.models.user import User
from src.models.project import Project
from src.models.task import Task
from src.models.organization import Organization


def convert_decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    return obj


class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: str,
        org_id: Optional[uuid.UUID] = None,
        data: Optional[dict] = None
    ) -> Notification:
        """Create a new notification"""
        # Convert Decimal values in data to float
        clean_data = convert_decimal_to_float(data or {})
        
        notification = Notification(
            user_id=user_id,
            org_id=org_id,
            type=notification_type,
            title=title,
            message=message,
            data=clean_data,
            is_read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def create_activity(
        db: Session,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
        action: str,
        description: str,
        project_id: Optional[uuid.UUID] = None,
        task_id: Optional[uuid.UUID] = None,
        extra_info: Optional[dict] = None
    ) -> ActivityLog:
        """Create an activity log entry"""
        clean_info = convert_decimal_to_float(extra_info or {})
        
        activity = ActivityLog(
            user_id=user_id,
            org_id=org_id,
            project_id=project_id,
            task_id=task_id,
            action=action,
            description=description,
            extra_info=clean_info
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def notify_task_assigned(db: Session, task: Task, project: Project, assigned_to: uuid.UUID, assigned_by_name: str):
        """Send notification when a user is assigned to a task"""
        message = f"{assigned_by_name} assigned you to task '{task.title}' in project '{project.title}'"
        
        NotificationService.create_notification(
            db=db,
            user_id=assigned_to,
            notification_type="task_assigned",
            title="New Task Assignment",
            message=message,
            org_id=project.org_id,
            data={"task_id": str(task.id), "project_id": str(project.id), "due_date": str(task.due_date)}
        )
        
        NotificationService.create_activity(
            db=db,
            user_id=assigned_to,
            org_id=project.org_id,
            project_id=project.id,
            task_id=task.id,
            action="task_assigned",
            description=f"Task '{task.title}' was assigned to {assigned_by_name}",
            extra_info={"assigned_by": assigned_by_name, "task_title": task.title}
        )

    @staticmethod
    def notify_task_status_change(
        db: Session,
        task: Task,
        project: Project,
        old_status: str,
        new_status: str,
        changed_by_name: str,
        assignee_ids: List[uuid.UUID]
    ):
        """Send notification when task status changes"""
        message = f"{changed_by_name} changed task '{task.title}' status from {old_status} to {new_status}"
        
        for user_id in assignee_ids:
            NotificationService.create_notification(
                db=db,
                user_id=user_id,
                notification_type="task_status_change",
                title=f"Task Status Changed: {task.title}",
                message=message,
                org_id=project.org_id,
                data={"task_id": str(task.id), "project_id": str(project.id), "old_status": old_status, "new_status": new_status}
            )
        
        NotificationService.create_activity(
            db=db,
            user_id=task.created_by,
            org_id=project.org_id,
            project_id=project.id,
            task_id=task.id,
            action="task_status_changed",
            description=f"Task '{task.title}' status changed from {old_status} to {new_status}",
            extra_info={"old_status": old_status, "new_status": new_status, "changed_by": changed_by_name}
        )

    @staticmethod
    def notify_task_overdue(db: Session, task: Task, project: Project, assignee_ids: List[uuid.UUID]):
        """Send notification when a task becomes overdue"""
        message = f"Task '{task.title}' in project '{project.title}' is overdue (due date: {task.due_date})"
        
        for user_id in assignee_ids:
            NotificationService.create_notification(
                db=db,
                user_id=user_id,
                notification_type="task_overdue",
                title="Task Overdue",
                message=message,
                org_id=project.org_id,
                data={"task_id": str(task.id), "project_id": str(project.id), "due_date": str(task.due_date)}
            )

    @staticmethod
    def notify_member_invited(db: Session, org: Organization, invited_email: str, invited_by_name: str, role: str):
        """Send notification when a member is invited"""
        NotificationService.create_activity(
            db=db,
            user_id=org.owner_id,
            org_id=org.id,
            action="member_invited",
            description=f"Invitation sent to {invited_email} as {role}",
            extra_info={"invited_email": invited_email, "role": role, "invited_by": invited_by_name}
        )

    @staticmethod
    def notify_member_joined(db: Session, org: Organization, user_id: uuid.UUID, user_name: str):
        """Send notification when a member joins via invite"""
        NotificationService.create_notification(
            db=db,
            user_id=org.owner_id,
            notification_type="member_joined",
            title="New Team Member",
            message=f"{user_name} has joined the organization",
            org_id=org.id,
            data={"user_id": str(user_id), "user_name": user_name}
        )
        
        NotificationService.create_activity(
            db=db,
            user_id=user_id,
            org_id=org.id,
            action="member_joined",
            description=f"{user_name} joined the organization",
            extra_info={"user_name": user_name}
        )


notification_service = NotificationService()