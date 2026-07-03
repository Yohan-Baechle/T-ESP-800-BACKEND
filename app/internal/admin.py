from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.core.auth import CurrentNurse
from app.dependencies import DbSession
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogPublic

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/audit-logs", response_model=list[AuditLogPublic])
def list_audit_logs(
    current: CurrentNurse,
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[AuditLog]:
    """Consulte le journal d'audit, du plus récent au plus ancien (CDC F6.5)."""
    return list(
        db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit))
    )
