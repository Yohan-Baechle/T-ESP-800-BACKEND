import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import UserStatus


class User(Base):
    """Compte utilisateur — entité racine du MLD (table `users`).

    `nurse` en hérite par identité de clé (Joined Table Inheritance, Merise).
    Les champs `email` / `hashed_password` sont ajoutés pour l'authentification
    (CDC F6.1), non représentés au niveau conceptuel du MLD.
    """

    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    totp_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"), default=UserStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __mapper_args__ = {"polymorphic_identity": "user"}


class Nurse(User):
    """Infirmier — hérite de `users` via `user_id` (PK = FK), conforme MLD.

    `replacement_nurse` distingue titulaire (False) et remplaçant (True),
    correspondant à la gestion des rôles du CDC (F1.6).
    """

    __tablename__ = "nurse"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True
    )
    order_number: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    last_name: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255))
    replacement_nurse: Mapped[bool] = mapped_column(Boolean, default=False)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    siret: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "nurse"}
