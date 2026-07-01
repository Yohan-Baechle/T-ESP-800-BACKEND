import uuid

from pydantic import BaseModel, Field

from app.models.enums import NursingOfficeStatus


class NursingOfficeCreate(BaseModel):
    """Données de création d'un cabinet (CDC F1.6 / WBS 1.4)."""

    nursing_office_name: str = Field(min_length=1, max_length=255)
    siret: int | None = None


class NursingOfficePublic(BaseModel):
    """Représentation publique d'un cabinet."""

    nursing_office_id: uuid.UUID
    nursing_office_name: str
    siret: int | None
    status: NursingOfficeStatus

    model_config = {"from_attributes": True}
