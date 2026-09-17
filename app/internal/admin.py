from fastapi import APIRouter
from sqlalchemy import select

from app.core.auth import CurrentAdmin
from app.core.pagination import paginate
from app.dependencies import DbSession, PaginationParams
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogPublic
from app.schemas.pagination import Page
from app.services.audit import log_event
from app.services.purge import purge_expired_transmissions

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/audit-logs", response_model=Page[AuditLogPublic])
def list_audit_logs(
    current: CurrentAdmin, db: DbSession, pagination: PaginationParams
) -> Page[AuditLogPublic]:
    """Consulte le journal d'audit, du plus récent au plus ancien (CDC F6.5)."""
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    return paginate(db, query, pagination)


@router.post("/purge-transmissions")
def purge_transmissions(current: CurrentAdmin, db: DbSession) -> dict[str, int]:
    """Purge les transmissions expirées — conservation RGPD (CDC F6.4)."""
    deleted = purge_expired_transmissions(db)
    log_event(
        "transmissions.purged",
        user_id=current.user_id,
        status_code=deleted,
        db=db,
    )
    return {"deleted": deleted}
