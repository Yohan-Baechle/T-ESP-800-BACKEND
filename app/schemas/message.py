import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """Ouverture d'une conversation avec un autre infirmier (CDC F4.1)."""

    recipient_id: uuid.UUID


class ConversationPublic(BaseModel):
    """Représentation d'une conversation."""

    conversation_id: uuid.UUID
    participant_a: uuid.UUID
    participant_b: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    """Envoi d'un message texte (CDC F4.1 / US-05)."""

    content: str = Field(min_length=1, max_length=5000)


class MessagePublic(BaseModel):
    """Représentation d'un message."""

    message_id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
