from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select

from app.core.auth import CurrentNurse
from app.core.config import get_settings
from app.core.storage import save_document
from app.dependencies import DbSession
from app.models.document import Document
from app.models.enums import DocumentType
from app.schemas.document import DocumentPublic

settings = get_settings()

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_CONTENT_TYPE = "application/pdf"


@router.post(
    "",
    response_model=DocumentPublic,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    current: CurrentNurse,
    db: DbSession,
    document_type: DocumentType = Form(),
    file: UploadFile = File(),
) -> Document:
    """Téléverse un document légal (CDC F1.2 : PDF, max 5 Mo)."""
    if file.content_type != ALLOWED_CONTENT_TYPE:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Seuls les fichiers PDF sont acceptés.",
        )

    content = await file.read()
    if len(content) > settings.max_document_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Le document dépasse la taille maximale de 5 Mo.",
        )

    file_path = save_document(content, file.filename or "document.pdf")
    document = Document(
        user_id=current.user_id,
        document_type=document_type,
        file_path=file_path,
        original_filename=file.filename or "document.pdf",
        size_bytes=len(content),
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentPublic])
def list_documents(current: CurrentNurse, db: DbSession) -> list[Document]:
    """Liste les documents légaux de l'infirmier authentifié (CDC F1.2)."""
    return list(
        db.scalars(select(Document).where(Document.user_id == current.user_id))
    )
