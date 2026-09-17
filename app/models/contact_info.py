import uuid

from geoalchemy2 import Geography
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ContactInfo(Base):
    """Coordonnées d'un cabinet, avec localisation géographique (MLD : contact_info).

    Le point géographique (WGS84) alimente la recherche par distance (CDC F2.3).
    """

    __tablename__ = "contact_info"

    contact_info_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nursing_office_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("nursing_office.nursing_office_id"),
        unique=True,
        index=True,
    )
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    postcode: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str] = mapped_column(Geography(geometry_type="POINT", srid=4326))
