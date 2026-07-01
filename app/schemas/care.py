import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class CareCreate(BaseModel):
    """Création d'un type de soin (CDC F2.1)."""

    care_name: str = Field(min_length=1, max_length=255)
    cotation_ngap: str | None = Field(default=None, max_length=50)
    description: str | None = None
    prescription_necessary: bool = False
    price: Decimal | None = Field(default=None, ge=0)


class CarePublic(BaseModel):
    """Représentation d'un type de soin."""

    care_id: uuid.UUID
    care_name: str
    cotation_ngap: str | None
    description: str | None
    prescription_necessary: bool
    price: Decimal | None

    model_config = {"from_attributes": True}
