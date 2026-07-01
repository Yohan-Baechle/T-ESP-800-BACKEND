from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.auth import CurrentNurse
from app.dependencies import DbSession
from app.models.care import Care
from app.schemas.care import CareCreate, CarePublic

router = APIRouter(prefix="/cares", tags=["cares"])


@router.post("", response_model=CarePublic, status_code=status.HTTP_201_CREATED)
def create_care(payload: CareCreate, current: CurrentNurse, db: DbSession) -> Care:
    """Ajoute un type de soin au référentiel (CDC F2.1)."""
    existing = db.scalar(select(Care).where(Care.care_name == payload.care_name))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce type de soin existe déjà.",
        )
    care = Care(**payload.model_dump())
    db.add(care)
    db.commit()
    db.refresh(care)
    return care


@router.get("", response_model=list[CarePublic])
def list_cares(current: CurrentNurse, db: DbSession) -> list[Care]:
    """Liste les types de soins disponibles (CDC F2.1)."""
    return list(db.scalars(select(Care).order_by(Care.care_name)))
