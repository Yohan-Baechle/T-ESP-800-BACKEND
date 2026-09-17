import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import ApplicationDecision, ApplicationStatus


class Apply(Base):
    """Candidature d'un remplaçant à une offre (MLD : apply / CDC F3.3).

    Table d'association nurse ↔ offer, clé primaire composée.
    """

    __tablename__ = "apply"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nurse.user_id"), primary_key=True
    )
    offer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("offer.offer_id"), primary_key=True
    )
    application_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.SUBMITTED,
    )
    decision: Mapped[ApplicationDecision] = mapped_column(
        Enum(ApplicationDecision, name="application_decision"),
        default=ApplicationDecision.PENDING,
    )
    decision_comment: Mapped[str | None] = mapped_column(String(512), nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
