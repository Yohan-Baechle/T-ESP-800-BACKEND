from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.auth import CurrentNurse
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.core.totp import generate_secret, provisioning_uri, verify_code
from app.dependencies import DbSession
from app.models.enums import UserStatus
from app.models.user import Nurse
from app.schemas.auth import (
    LoginRequest,
    NursePublic,
    NurseRegister,
    Token,
    TwoFactorCode,
    TwoFactorSetup,
)
from app.services.ordre_verification import verify_order_number

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

    if not verify_order_number(payload.order_number):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Numéro Ordre Infirmiers invalide.",
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
        status=UserStatus.ACTIVE,
    )
    db.add(nurse)
    db.commit()
    db.refresh(nurse)
    return nurse


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: DbSession) -> Token:
    """Authentifie un infirmier et renvoie un jeton JWT (CDC F6.1).

    Si la double authentification est activée, un code TOTP valide est requis.
    """
    nurse = db.scalar(select(Nurse).where(Nurse.email == payload.email))
    if nurse is None or not verify_password(payload.password, nurse.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides.",
        )

    if nurse.two_factor_enabled:
        if payload.otp_code is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Code de double authentification requis.",
            )
        if nurse.totp_secret is None or not verify_code(
            nurse.totp_secret, payload.otp_code
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Code de double authentification invalide.",
            )

    return Token(access_token=create_access_token(str(nurse.user_id)))


@router.get("/me", response_model=NursePublic)
def read_current_nurse(current: CurrentNurse) -> Nurse:
    """Retourne le profil de l'infirmier authentifié (US-01)."""
    return current


@router.post("/2fa/setup", response_model=TwoFactorSetup)
def setup_two_factor(current: CurrentNurse, db: DbSession) -> TwoFactorSetup:
    """Génère un secret TOTP pour activer la double authentification (CDC F1.4)."""
    secret = generate_secret()
    current.totp_secret = secret
    db.commit()
    return TwoFactorSetup(
        secret=secret,
        provisioning_uri=provisioning_uri(secret, current.email),
    )


@router.post("/2fa/enable", status_code=status.HTTP_204_NO_CONTENT)
def enable_two_factor(
    payload: TwoFactorCode, current: CurrentNurse, db: DbSession
) -> None:
    """Active la double authentification après vérification d'un code (CDC F1.4)."""
    if current.totp_secret is None or not verify_code(
        current.totp_secret, payload.otp_code
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code invalide ou secret non initialisé.",
        )
    current.two_factor_enabled = True
    db.commit()


@router.post("/2fa/disable", status_code=status.HTTP_204_NO_CONTENT)
def disable_two_factor(current: CurrentNurse, db: DbSession) -> None:
    """Désactive la double authentification (CDC F1.4)."""
    current.two_factor_enabled = False
    current.totp_secret = None
    db.commit()
