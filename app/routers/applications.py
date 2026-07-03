import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, update

from app.core.auth import CurrentNurse
from app.core.pagination import paginate
from app.dependencies import DbSession, PaginationParams
from app.models.application import Apply
from app.models.enums import (
    ApplicationDecision,
    ApplicationStatus,
    OfferStatus,
)
from app.models.nursing_office import belong
from app.models.offer import Offer
from app.schemas.application import (
    ApplicationCreate,
    ApplicationDecisionUpdate,
    ApplicationPublic,
)
from app.schemas.pagination import Page

router = APIRouter(prefix="/offers", tags=["applications"])


def _get_offer_or_404(offer_id: uuid.UUID, db: DbSession) -> Offer:
    offer = db.get(Offer, offer_id)
    if offer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable."
        )
    return offer


def _require_office_member(
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
            detail="Vous n'êtes pas rattaché au cabinet de cette offre.",
        )


@router.post(
    "/{offer_id}/apply",
    response_model=ApplicationPublic,
    status_code=status.HTTP_201_CREATED,
)
def apply_to_offer(
    offer_id: uuid.UUID,
    payload: ApplicationCreate,
    current: CurrentNurse,
    db: DbSession,
) -> Apply:
    """Postule à une offre de remplacement (CDC F3.3 / US-03)."""
    offer = _get_offer_or_404(offer_id, db)
    if offer.status != OfferStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette offre n'accepte plus de candidatures.",
        )
    if offer.created_by == current.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas postuler à votre propre offre.",
        )
    if db.get(Apply, (current.user_id, offer_id)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vous avez déjà postulé à cette offre.",
        )

    application = Apply(
        user_id=current.user_id,
        offer_id=offer_id,
        application_message=payload.application_message,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/{offer_id}/applications", response_model=Page[ApplicationPublic])
def list_applications(
    offer_id: uuid.UUID,
    current: CurrentNurse,
    db: DbSession,
    pagination: PaginationParams,
) -> Page[ApplicationPublic]:
    """Liste les candidatures reçues pour une offre (CDC F3.3 / US-04)."""
    offer = _get_offer_or_404(offer_id, db)
    _require_office_member(offer.nursing_office_id, current.user_id, db)
    query = select(Apply).where(Apply.offer_id == offer_id)
    return paginate(db, query, pagination)


@router.patch(
    "/{offer_id}/applications/{applicant_id}",
    response_model=ApplicationPublic,
)
def decide_application(
    offer_id: uuid.UUID,
    applicant_id: uuid.UUID,
    payload: ApplicationDecisionUpdate,
    current: CurrentNurse,
    db: DbSession,
) -> Apply:
    """Accepte ou refuse une candidature (CDC F3.3 / US-04)."""
    offer = _get_offer_or_404(offer_id, db)
    _require_office_member(offer.nursing_office_id, current.user_id, db)

    application = db.get(Apply, (applicant_id, offer_id))
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidature introuvable."
        )

    application.decision = payload.decision
    application.decision_comment = payload.decision_comment
    application.status = ApplicationStatus.REVIEWED
    application.reviewed_by = current.user_id

    if payload.decision == ApplicationDecision.ACCEPTED:
        offer.status = OfferStatus.CLOSED
        db.execute(
            update(Apply)
            .where(
                Apply.offer_id == offer_id,
                Apply.user_id != applicant_id,
                Apply.decision == ApplicationDecision.PENDING,
            )
            .values(
                decision=ApplicationDecision.REJECTED,
                status=ApplicationStatus.REVIEWED,
                reviewed_by=current.user_id,
            )
        )

    db.commit()
    db.refresh(application)
    return application
