import uuid

from pydantic import BaseModel, Field


class ContactInfoUpsert(BaseModel):
    """Coordonnées et localisation d'un cabinet (CDC F2.3)."""

    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=255)
    postcode: int | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class ContactInfoPublic(BaseModel):
    """Représentation des coordonnées d'un cabinet."""

    contact_info_id: uuid.UUID
    nursing_office_id: uuid.UUID
    address: str | None
    city: str | None
    postcode: int | None
    latitude: float
    longitude: float
