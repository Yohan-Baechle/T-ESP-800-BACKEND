import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.auth import CurrentNurse
from app.core.config import get_settings
from app.dependencies import DbSession
from app.models.enums import PatientStatus, TransmissionStatus
from app.models.patient import Patient, Transmission
from app.schemas.patient import (
    PatientCreate,
    PatientPublic,
    TransmissionCreate,
    TransmissionPublic,
)
from app.services.audit import log_event

settings = get_settings()

router = APIRouter(prefix="/patients", tags=["patients"])


def _get_active_patient(patient_id: uuid.UUID, db: DbSession) -> Patient:
    patient = db.get(Patient, patient_id)
    if patient is None or patient.status == PatientStatus.ANONYMIZED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient introuvable."
        )
    return patient


@router.post("", response_model=PatientPublic, status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate, current: CurrentNurse, db: DbSession
) -> Patient:
    """Crée un dossier patient (CDC F4.3)."""
    patient = Patient(
        last_name=payload.last_name,
        first_name=payload.first_name,
        birth_date=payload.birth_date,
        note=payload.note,
        created_by=current.user_id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("", response_model=list[PatientPublic])
def list_patients(current: CurrentNurse, db: DbSession) -> list[Patient]:
    """Liste les dossiers patients actifs (CDC F4.3)."""
    return list(
        db.scalars(select(Patient).where(Patient.status == PatientStatus.ACTIVE))
    )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def anonymize_patient(
    patient_id: uuid.UUID, current: CurrentNurse, db: DbSession
) -> None:
    """Anonymise un dossier patient — droit à l'oubli RGPD (CDC F6.4)."""
    patient = _get_active_patient(patient_id, db)
    patient.last_name = None
    patient.first_name = None
    patient.birth_date = None
    patient.note = None
    patient.status = PatientStatus.ANONYMIZED
    patient.updated_by = current.user_id
    db.commit()
    log_event(
        "patient.anonymized", user_id=current.user_id, path=str(patient_id), db=db
    )


@router.post(
    "/{patient_id}/transmissions",
    response_model=TransmissionPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_transmission(
    patient_id: uuid.UUID,
    payload: TransmissionCreate,
    current: CurrentNurse,
    db: DbSession,
) -> Transmission:
    """Transmet des informations patient (CDC F4.3 / US-10).

    La transmission expire après la durée de conservation RGPD (F6.4).
    """
    _get_active_patient(patient_id, db)
    expires_at = datetime.now(UTC) + timedelta(
        days=settings.transmission_retention_days
    )
    transmission = Transmission(
        patient_id=patient_id,
        text=payload.text,
        created_by=current.user_id,
        expires_at=expires_at,
    )
    db.add(transmission)
    db.commit()
    db.refresh(transmission)
    log_event(
        "transmission.created", user_id=current.user_id, path=str(patient_id), db=db
    )
    return transmission


@router.get("/{patient_id}/transmissions", response_model=list[TransmissionPublic])
def list_transmissions(
    patient_id: uuid.UUID, current: CurrentNurse, db: DbSession
) -> list[Transmission]:
    """Liste les transmissions actives et non expirées d'un patient (CDC F4.3)."""
    _get_active_patient(patient_id, db)
    now = datetime.now(UTC)
    return list(
        db.scalars(
            select(Transmission).where(
                Transmission.patient_id == patient_id,
                Transmission.status == TransmissionStatus.ACTIVE,
                Transmission.expires_at > now,
            )
        )
    )
