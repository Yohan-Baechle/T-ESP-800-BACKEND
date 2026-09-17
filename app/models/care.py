import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Column, ForeignKey, Numeric, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

offer_care = Table(
    "offer_care",
    Base.metadata,
    Column("offer_id", ForeignKey("offer.offer_id"), primary_key=True),
    Column("care_id", ForeignKey("care.care_id"), primary_key=True),
)


class Care(Base):
    """Type de soin infirmier (MLD : care / CDC F2.1).

    Sert de référentiel pour filtrer les offres par type de soins requis.
    """

    __tablename__ = "care"

    care_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    care_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    cotation_ngap: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    prescription_necessary: Mapped[bool] = mapped_column(Boolean, default=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
