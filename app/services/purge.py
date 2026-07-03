from datetime import UTC, datetime

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.patient import Transmission


def purge_expired_transmissions(db: Session) -> int:
    """Supprime définitivement les transmissions expirées (CDC F6.4).

    Retourne le nombre de transmissions supprimées. La suppression physique
    (et non le simple masquage) satisfait la durée de conservation RGPD.
    """
    result = db.execute(
        delete(Transmission).where(Transmission.expires_at <= datetime.now(UTC))
    )
    db.commit()
    return result.rowcount
