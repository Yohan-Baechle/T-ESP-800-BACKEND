import uuid

from fastapi import APIRouter, HTTPException, status
from geoalchemy2 import WKTElement
from geoalchemy2.functions import ST_X, ST_Y
from sqlalchemy import select

from app.core.auth import CurrentNurse
from app.dependencies import DbSession
from app.models.contact_info import ContactInfo
from app.models.nursing_office import NursingOffice, belong
from app.schemas.contact_info import ContactInfoPublic, ContactInfoUpsert
from app.schemas.nursing_office import NursingOfficeCreate, NursingOfficePublic

router = APIRouter(prefix="/nursing-offices", tags=["nursing-offices"])


def _require_membership(
    nursing_office_id: uuid.UUID, user_id: uuid.UUID, db: DbSession
) -> None:
    membership = db.scalar(
        select(belong.c.user_id).where(
            belong.c.user_id == user_id,
            belong.c.nursing_office_id == nursing_office_id,
        )
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas rattaché à ce cabinet.",
        )


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


def _contact_info_response(contact: ContactInfo, db: DbSession) -> ContactInfoPublic:
    longitude, latitude = db.execute(
        select(ST_X(contact.location), ST_Y(contact.location))
    ).one()
    return ContactInfoPublic(
        contact_info_id=contact.contact_info_id,
        nursing_office_id=contact.nursing_office_id,
        address=contact.address,
        city=contact.city,
        postcode=contact.postcode,
        latitude=latitude,
        longitude=longitude,
    )


@router.put("/{nursing_office_id}/contact-info", response_model=ContactInfoPublic)
def upsert_contact_info(
    nursing_office_id: uuid.UUID,
    payload: ContactInfoUpsert,
    current: CurrentNurse,
    db: DbSession,
) -> ContactInfoPublic:
    """Définit l'adresse et la localisation d'un cabinet (CDC F2.3)."""
    _require_membership(nursing_office_id, current.user_id, db)

    point = WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326)
    contact = db.scalar(
        select(ContactInfo).where(ContactInfo.nursing_office_id == nursing_office_id)
    )
    if contact is None:
        contact = ContactInfo(nursing_office_id=nursing_office_id, location=point)
        db.add(contact)
    else:
        contact.location = point

    contact.address = payload.address
    contact.city = payload.city
    contact.postcode = payload.postcode
    db.commit()
    db.refresh(contact)
    return _contact_info_response(contact, db)
