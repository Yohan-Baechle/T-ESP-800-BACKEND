import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import PatientStatus, TransmissionStatus


class Patient(Base):
    """Dossier patient (MLD : patient / CDC F4.3).

    Données de santé sensibles : traçabilité (created_by/updated_by) et
    anonymisation possible au titre du droit à l'oubli RGPD (F6.4).
    """

    __tablename__ = "patient"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PatientStatus] = mapped_column(
        Enum(PatientStatus, name="patient_status"), default=PatientStatus.ACTIVE
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Transmission(Base):
    """Transmission d'informations patient (MLD : transmission / CDC F4.3).

    Soumise à une durée de conservation (expires_at) au titre du RGPD (F6.4).
    """

    __tablename__ = "transmission"

    transmission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient.patient_id"), index=True
    )
    text: Mapped[str] = mapped_column(Text)
    status: Mapped[TransmissionStatus] = mapped_column(
        Enum(TransmissionStatus, name="transmission_status"),
        default=TransmissionStatus.ACTIVE,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
