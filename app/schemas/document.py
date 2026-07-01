import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import DocumentStatus, DocumentType


class DocumentPublic(BaseModel):
    """Représentation d'un document légal (sans le binaire)."""

    document_id: uuid.UUID
    document_type: DocumentType
    status: DocumentStatus
    original_filename: str
    size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}
