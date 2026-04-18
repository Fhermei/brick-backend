"""
KPI Service - Calculate KPI metrics and trigger notifications
"""

from sqlalchemy.orm import Session
import uuid
from typing import Optional
from src.models.kpi import KPI
from src.models.project import Project
from src.core.kpi import compute_kar, get_kar_status


class KPIService:
    @staticmethod
    def calculate_and_update_kpi(db: Session, kpi_id: uuid.UUID) -> Optional[KPI]:
        """Calculate KAR and update KPI status"""
        kpi = db.query(KPI).filter(KPI.id == kpi_id).first()
        if not kpi:
            return None
        
        # Calculate KAR
        if kpi.actual_value and kpi.target_value:
            kar = compute_kar(float(kpi.actual_value), float(kpi.target_value))
            kpi.kar = kar
            kar_status = get_kar_status(kar)
            kpi.status = kar_status["status"]
        else:
            kpi.kar = 0
            kpi.status = "critical"
        
        db.commit()
        db.refresh(kpi)
        return kpi

    @staticmethod
    def check_kpi_thresholds(db: Session, kpi: KPI, project: Project):
        """Check KPI thresholds and create notifications"""
        from src.services.notification_service import notification_service
        
        if kpi.kar is None:
            return
        
        if kpi.kar < 50:
            # Critical - notify project owner and org admin
            notification_service.create_notification(
                db=db,
                user_id=project.created_by,
                notification_type="kpi_critical",
                title=f"KPI Critical: {kpi.indicator_name}",
                message=f"KPI '{kpi.indicator_name}' is at {kpi.kar}% - below 50% target. Immediate action required.",
                org_id=project.org_id,
                data={"kpi_id": str(kpi.id), "project_id": str(project.id), "kar": kpi.kar}
            )
        elif kpi.kar < 75:
            # Warning - notify project owner
            notification_service.create_notification(
                db=db,
                user_id=project.created_by,
                notification_type="kpi_warning",
                title=f"KPI Warning: {kpi.indicator_name}",
                message=f"KPI '{kpi.indicator_name}' is at {kpi.kar}% - below 75% target. Needs attention.",
                org_id=project.org_id,
                data={"kpi_id": str(kpi.id), "project_id": str(project.id), "kar": kpi.kar}
            )


kpi_service = KPIService()