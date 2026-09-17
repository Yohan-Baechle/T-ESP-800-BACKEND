import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.core.auth import CurrentNurse
from app.core.pagination import paginate
from app.dependencies import DbSession, PaginationParams
from app.models.message import Conversation, Message
from app.models.user import Nurse
from app.schemas.message import (
    ConversationCreate,
    ConversationPublic,
    MessageCreate,
    MessagePublic,
)
from app.schemas.pagination import Page

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _normalize_pair(x: uuid.UUID, y: uuid.UUID) -> tuple[uuid.UUID, uuid.UUID]:
    return (x, y) if str(x) < str(y) else (y, x)


def _get_conversation_for_member(
    conversation_id: uuid.UUID, user_id: uuid.UUID, db: DbSession
) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation introuvable."
        )
    if user_id not in (conversation.participant_a, conversation.participant_b):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne participez pas à cette conversation.",
        )
    return conversation


@router.post("", response_model=ConversationPublic, status_code=status.HTTP_201_CREATED)
def open_conversation(
    payload: ConversationCreate, current: CurrentNurse, db: DbSession
) -> Conversation:
    """Ouvre (ou récupère) une conversation avec un autre infirmier (CDC F4.1)."""
    if payload.recipient_id == current.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible d'ouvrir une conversation avec soi-même.",
        )
    if db.get(Nurse, payload.recipient_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destinataire introuvable."
        )

    a, b = _normalize_pair(current.user_id, payload.recipient_id)
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.participant_a == a, Conversation.participant_b == b
        )
    )
    if conversation is None:
        conversation = Conversation(participant_a=a, participant_b=b)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    return conversation


@router.get("", response_model=list[ConversationPublic])
def list_conversations(current: CurrentNurse, db: DbSession) -> list[Conversation]:
    """Liste les conversations de l'infirmier courant (CDC F4.1)."""
    return list(
        db.scalars(
            select(Conversation).where(
                or_(
                    Conversation.participant_a == current.user_id,
                    Conversation.participant_b == current.user_id,
                )
            )
        )
    )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessagePublic,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    conversation_id: uuid.UUID,
    payload: MessageCreate,
    current: CurrentNurse,
    db: DbSession,
) -> Message:
    """Envoie un message dans une conversation (CDC F4.1 / US-05)."""
    _get_conversation_for_member(conversation_id, current.user_id, db)
    message = Message(
        conversation_id=conversation_id,
        sender_id=current.user_id,
        content=payload.content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/{conversation_id}/messages", response_model=Page[MessagePublic])
def list_messages(
    conversation_id: uuid.UUID,
    current: CurrentNurse,
    db: DbSession,
    pagination: PaginationParams,
) -> Page[MessagePublic]:
    """Liste les messages d'une conversation (CDC F4.1)."""
    _get_conversation_for_member(conversation_id, current.user_id, db)
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return paginate(db, query, pagination)
