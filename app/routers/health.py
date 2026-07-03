from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.dependencies import DbSession

router = APIRouter(tags=["health"])


@router.get("/health")
def liveness() -> dict[str, str]:
    """Vérifie que l'application répond (liveness)."""
    return {"status": "ok"}


@router.get("/health/ready")
def readiness(db: DbSession, response: Response) -> dict[str, str]:
    """Vérifie que l'application et la base de données sont prêtes (readiness)."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable", "database": "down"}
    return {"status": "ok", "database": "up"}
