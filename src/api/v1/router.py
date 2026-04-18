"""
v1 API router — mounts all endpoint sub-routers.
"""

from fastapi import APIRouter

from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.organizations import router as org_router
from src.api.v1.endpoints.dashboard import router as dashboard_router
from src.api.v1.endpoints.projects import router as projects_router
from src.api.v1.endpoints.tasks import router as tasks_router
from src.api.v1.endpoints.team import router as team_router
from src.api.v1.endpoints.comments import router as comments_router
from src.api.v1.endpoints.notifications import router as notifications_router
from src.api.v1.endpoints.activities import router as activities_router
from src.api.v1.endpoints.expenses import router as expenses_router
from src.api.v1.endpoints.budget import router as budget_router
from src.api.v1.endpoints.kpis import router as kpis_router
from src.api.v1.endpoints.reports import router as reports_router
from src.api.v1.endpoints.audit import router as audit_router
from src.api.v1.endpoints.expenses import router as expenses_router

router = APIRouter()

# Health check
@router.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Brick API is alive"}

# Mount all routers
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(org_router, prefix="/organizations", tags=["Organizations"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(projects_router, prefix="/projects", tags=["Projects"])
router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
router.include_router(team_router, prefix="/team", tags=["Team"])
router.include_router(comments_router, prefix="/comments", tags=["Comments"])
router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
router.include_router(activities_router, prefix="/activities", tags=["Activities"])
router.include_router(expenses_router, prefix="/expenses", tags=["Expenses"])
router.include_router(budget_router, prefix="/budget", tags=["Budget"])
router.include_router(kpis_router, prefix="/kpis", tags=["KPIs"])
router.include_router(reports_router, prefix="/reports", tags=["Reports"])
router.include_router(audit_router, prefix="/audit", tags=["Audit"])
router.include_router(expenses_router, prefix="/expenses", tags=["Expenses"])