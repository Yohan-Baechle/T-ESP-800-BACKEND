from fastapi import APIRouter
from sqlalchemy import select

from app.core.auth import CurrentNurse
from app.dependencies import DbSession
from app.models.application import Apply
from app.models.nursing_office import belong
from app.models.offer import Offer
from app.schemas.application import ApplicationPublic
from app.schemas.offer import OfferPublic

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/applications", response_model=list[ApplicationPublic])
def list_my_applications(current: CurrentNurse, db: DbSession) -> list[Apply]:
    """Liste les candidatures déposées par l'infirmier courant (CDC F3.5 / US-09)."""
    return list(db.scalars(select(Apply).where(Apply.user_id == current.user_id)))


@router.get("/offers", response_model=list[OfferPublic])
def list_my_offers(current: CurrentNurse, db: DbSession) -> list[Offer]:
    """Liste les offres des cabinets de l'infirmier courant (CDC F3.5 / US-07)."""
    return list(
        db.scalars(
            select(Offer)
            .join(
                belong,
                belong.c.nursing_office_id == Offer.nursing_office_id,
            )
            .where(belong.c.user_id == current.user_id)
        )
    )
