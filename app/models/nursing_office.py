import uuid

from sqlalchemy import BigInteger, Column, Enum, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import NursingOfficeStatus

belong = Table(
    "belong",
    Base.metadata,
    Column("user_id", ForeignKey("nurse.user_id"), primary_key=True),
    Column(
        "nursing_office_id",
        ForeignKey("nursing_office.nursing_office_id"),
        primary_key=True,
    ),
)


class NursingOffice(Base):
    """Cabinet infirmier (MLD : nursing_office).

    Un cabinet publie des offres de remplacement (CDC F3.1). Le lien
    infirmiers ↔ cabinets est porté par la table d'association `belong`.
    """

    __tablename__ = "nursing_office"

    nursing_office_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nursing_office_name: Mapped[str] = mapped_column(String(255))
    siret: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[NursingOfficeStatus] = mapped_column(
        Enum(NursingOfficeStatus, name="nursing_office_status"),
        default=NursingOfficeStatus.ACTIVE,
    )
