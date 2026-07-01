import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Conversation(Base):
    """Fil de discussion entre deux infirmiers (CDC F4.1 / US-05).

    La paire (participant_a, participant_b) est unique et normalisée
    (participant_a < participant_b) pour éviter les doublons de conversation.
    """

    __tablename__ = "conversation"
    __table_args__ = (
        UniqueConstraint("participant_a", "participant_b", name="uq_conversation_pair"),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    participant_a: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nurse.user_id"), index=True
    )
    participant_b: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nurse.user_id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Message(Base):
    """Message texte au sein d'une conversation (CDC F4.1)."""

    __tablename__ = "message"

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation.conversation_id"),
        index=True,
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nurse.user_id")
    )
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
