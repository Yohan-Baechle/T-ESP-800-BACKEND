import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.enums import OfferStatus


class OfferCreate(BaseModel):
    """Données de publication d'une offre de remplacement (CDC F3.1)."""

    nursing_office_id: uuid.UUID
    start: datetime
    end: datetime
    estimated_turnover: Decimal | None = Field(default=None, ge=0)
    description: str | None = None
    valid_till: datetime | None = None

    @model_validator(mode="after")
    def _check_dates(self) -> "OfferCreate":
        if self.end <= self.start:
            raise ValueError("La date de fin doit être postérieure au début.")
        return self


class OfferPublic(BaseModel):
    """Représentation publique d'une offre."""

    offer_id: uuid.UUID
    nursing_office_id: uuid.UUID
    start: datetime
    end: datetime
    estimated_turnover: Decimal | None
    description: str | None
    status: OfferStatus
    valid_till: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
