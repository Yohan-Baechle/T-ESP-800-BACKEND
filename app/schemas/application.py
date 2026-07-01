import uuid

from pydantic import BaseModel, Field

from app.models.enums import ApplicationDecision, ApplicationStatus


class ApplicationCreate(BaseModel):
    """Dépôt d'une candidature à une offre (CDC F3.3 / US-03)."""

    application_message: str | None = Field(default=None, max_length=2000)


class ApplicationDecisionUpdate(BaseModel):
    """Décision du cabinet sur une candidature (CDC F3.3 / US-04)."""

    decision: ApplicationDecision
    decision_comment: str | None = Field(default=None, max_length=512)


class ApplicationPublic(BaseModel):
    """Représentation d'une candidature."""

    user_id: uuid.UUID
    offer_id: uuid.UUID
    application_message: str | None
    status: ApplicationStatus
    decision: ApplicationDecision
    decision_comment: str | None

    model_config = {"from_attributes": True}
