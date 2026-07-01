from fastapi import APIRouter, status
from sqlalchemy import select

from app.core.auth import CurrentNurse
from app.dependencies import DbSession
from app.models.nursing_office import NursingOffice, belong
from app.schemas.nursing_office import NursingOfficeCreate, NursingOfficePublic

router = APIRouter(prefix="/nursing-offices", tags=["nursing-offices"])


@router.post(
    "",
    response_model=NursingOfficePublic,
    status_code=status.HTTP_201_CREATED,
)
def create_nursing_office(
    payload: NursingOfficeCreate, current: CurrentNurse, db: DbSession
) -> NursingOffice:
    """Crée un cabinet et y rattache l'infirmier courant (CDC F1.6)."""
    office = NursingOffice(
        nursing_office_name=payload.nursing_office_name,
        siret=payload.siret,
    )
    db.add(office)
    db.flush()
    db.execute(
        belong.insert().values(
            user_id=current.user_id,
            nursing_office_id=office.nursing_office_id,
        )
    )
    db.commit()
    db.refresh(office)
    return office


@router.get("", response_model=list[NursingOfficePublic])
def list_my_nursing_offices(
    current: CurrentNurse, db: DbSession
) -> list[NursingOffice]:
    """Liste les cabinets auxquels l'infirmier courant est rattaché."""
    return list(
        db.scalars(
            select(NursingOffice)
            .join(belong, belong.c.nursing_office_id == NursingOffice.nursing_office_id)
            .where(belong.c.user_id == current.user_id)
        )
    )
