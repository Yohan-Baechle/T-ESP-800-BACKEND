from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.dependencies import DbSession
from app.models.user import Nurse
from app.schemas.auth import LoginRequest, NursePublic, NurseRegister, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=NursePublic,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: NurseRegister, db: DbSession) -> Nurse:
    """Inscrit un nouvel infirmier (CDC F1.1 / US-01)."""
    existing = db.scalar(select(Nurse).where(Nurse.email == payload.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà pour cet email.",
        )

    nurse = Nurse(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        order_number=payload.order_number,
        last_name=payload.last_name,
        first_name=payload.first_name,
        replacement_nurse=payload.replacement_nurse,
        company_name=payload.company_name,
        siret=payload.siret,
    )
    db.add(nurse)
    db.commit()
    db.refresh(nurse)
    return nurse


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: DbSession) -> Token:
    """Authentifie un infirmier et renvoie un jeton JWT (CDC F6.1)."""
    nurse = db.scalar(select(Nurse).where(Nurse.email == payload.email))
    if nurse is None or not verify_password(payload.password, nurse.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides.",
        )
    return Token(access_token=create_access_token(str(nurse.user_id)))
