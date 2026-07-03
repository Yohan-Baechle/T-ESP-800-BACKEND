import uuid

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.audit_log import AuditLog


def log_event(
    action: str,
    *,
    user_id: uuid.UUID | None = None,
    method: str | None = None,
    path: str | None = None,
    status_code: int | None = None,
    db: Session | None = None,
) -> None:
    """Journalise un événement d'audit (CDC F6.5).

    Si aucune session n'est fournie, une session dédiée est créée : l'écriture
    d'audit ne doit jamais faire échouer l'action métier appelante.
    """
    entry = AuditLog(
        action=action,
        user_id=user_id,
        method=method,
        path=path,
        status_code=status_code,
    )
    own_session = db is None
    session = db or SessionLocal()
    try:
        session.add(entry)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        if own_session:
            session.close()
