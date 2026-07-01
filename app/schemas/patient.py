import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import PatientStatus, TransmissionStatus


class PatientCreate(BaseModel):
    """Création d'un dossier patient (CDC F4.3)."""

    last_name: str = Field(min_length=1, max_length=255)
    first_name: str = Field(min_length=1, max_length=255)
    birth_date: date | None = None
    note: str | None = None


class PatientPublic(BaseModel):
    """Représentation d'un dossier patient."""

    patient_id: uuid.UUID
    last_name: str | None
    first_name: str | None
    birth_date: date | None
    note: str | None
    status: PatientStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class TransmissionCreate(BaseModel):
    """Dépôt d'une transmission patient (CDC F4.3 / US-10)."""

    text: str = Field(min_length=1, max_length=10000)


class TransmissionPublic(BaseModel):
    """Représentation d'une transmission patient."""

    transmission_id: uuid.UUID
    patient_id: uuid.UUID
    text: str
    status: TransmissionStatus
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}
