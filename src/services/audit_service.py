"""
Audit Service - Log all actions for compliance
"""

from sqlalchemy.orm import Session
import uuid
from typing import Optional, Any
from src.models.audit_log import AuditLog


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        action: str,
        entity_type: str,
        entity_id: Optional[uuid.UUID] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Create an audit log entry"""
        audit_log = AuditLog(
            org_id=org_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log


audit_service = AuditService()