import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from geoalchemy2 import WKTElement
from geoalchemy2.functions import ST_DWithin
from sqlalchemy import select

from app.core.auth import CurrentNurse
from app.dependencies import DbSession
from app.models.contact_info import ContactInfo
from app.models.enums import OfferStatus
from app.models.nursing_office import belong
from app.models.offer import Offer
from app.schemas.offer import OfferCreate, OfferPublic

router = APIRouter(prefix="/offers", tags=["offers"])


@router.post("", response_model=OfferPublic, status_code=status.HTTP_201_CREATED)
def publish_offer(payload: OfferCreate, current: CurrentNurse, db: DbSession) -> Offer:
    """Publie une offre de remplacement pour un cabinet (CDC F3.1 / US-02).

    L'infirmier doit être rattaché au cabinet pour publier en son nom.
    """
    is_member = db.scalar(
        select(belong.c.user_id).where(
            belong.c.user_id == current.user_id,
            belong.c.nursing_office_id == payload.nursing_office_id,
        )
    )
    if is_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas rattaché à ce cabinet.",
        )

    offer = Offer(
        nursing_office_id=payload.nursing_office_id,
        start=payload.start,
        end=payload.end,
        estimated_turnover=payload.estimated_turnover,
        description=payload.description,
        valid_till=payload.valid_till,
        created_by=current.user_id,
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


@router.get("", response_model=list[OfferPublic])
def list_open_offers(
    current: CurrentNurse,
    db: DbSession,
    start_after: Annotated[datetime | None, Query()] = None,
    end_before: Annotated[datetime | None, Query()] = None,
    min_turnover: Annotated[Decimal | None, Query(ge=0)] = None,
    nursing_office_id: Annotated[uuid.UUID | None, Query()] = None,
    near_lat: Annotated[float | None, Query(ge=-90, le=90)] = None,
    near_lon: Annotated[float | None, Query(ge=-180, le=180)] = None,
    radius_km: Annotated[float | None, Query(gt=0)] = None,
) -> list[Offer]:
    """Recherche les offres ouvertes selon des critères (CDC F2.1 / F2.3 / US-03)."""
    query = select(Offer).where(Offer.status == OfferStatus.OPEN)
    if start_after is not None:
        query = query.where(Offer.start >= start_after)
    if end_before is not None:
        query = query.where(Offer.end <= end_before)
    if min_turnover is not None:
        query = query.where(Offer.estimated_turnover >= min_turnover)
    if nursing_office_id is not None:
        query = query.where(Offer.nursing_office_id == nursing_office_id)

    geo_params = (near_lat, near_lon, radius_km)
    if any(p is not None for p in geo_params):
        if any(p is None for p in geo_params):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="near_lat, near_lon et radius_km sont requis ensemble.",
            )
        point = WKTElement(f"POINT({near_lon} {near_lat})", srid=4326)
        query = query.join(
            ContactInfo,
            ContactInfo.nursing_office_id == Offer.nursing_office_id,
        ).where(ST_DWithin(ContactInfo.location, point, radius_km * 1000))

    return list(db.scalars(query))
