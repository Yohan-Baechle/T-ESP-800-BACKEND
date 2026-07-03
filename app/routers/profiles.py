from fastapi import APIRouter

from app.core.auth import CurrentNurse
from app.dependencies import DbSession
from app.models.user import Nurse
from app.schemas.auth import NursePublic
from app.schemas.nurse import NurseUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=NursePublic)
def read_profile(current: CurrentNurse) -> Nurse:
    """Retourne le profil de l'infirmier authentifié (CDC F1.5)."""
    return current


@router.patch("/me", response_model=NursePublic)
def update_profile(payload: NurseUpdate, current: CurrentNurse, db: DbSession) -> Nurse:
    """Met à jour le profil de l'infirmier authentifié (CDC F1.5 / WBS 1.3)."""
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(current, field, value)
    db.commit()
    db.refresh(current)
    return current
