from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.dependencies import DbSession
from app.models.user import Nurse

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def get_current_nurse(
    token: Annotated[str, Depends(oauth2_scheme)], db: DbSession
) -> Nurse:
    """Résout l'infirmier authentifié à partir du jeton JWT (CDC F6.1)."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    subject = decode_access_token(token)
    if subject is None:
        raise credentials_error

    nurse = db.get(Nurse, subject)
    if nurse is None:
        raise credentials_error
    return nurse


CurrentNurse = Annotated[Nurse, Depends(get_current_nurse)]


def require_admin(current: CurrentNurse) -> Nurse:
    """Autorise uniquement les infirmiers administrateurs (CDC F6.5)."""
    if not current.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs.",
        )
    return current


CurrentAdmin = Annotated[Nurse, Depends(require_admin)]
