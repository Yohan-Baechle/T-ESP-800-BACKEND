import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditLogPublic(BaseModel):
    """Représentation d'une entrée du journal d'audit (CDC F6.5)."""

    audit_log_id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    method: str | None
    path: str | None
    status_code: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
