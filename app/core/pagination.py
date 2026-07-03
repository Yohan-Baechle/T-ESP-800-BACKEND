from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.dependencies import Pagination
from app.schemas.pagination import Page


def paginate(db: Session, query: Select, params: Pagination) -> Page:
    """Applique la pagination à une requête et retourne une page enveloppée.

    Compte le nombre total d'éléments puis retourne la tranche demandée
    (``limit`` / ``offset``).
    """
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(db.scalars(query.limit(params.limit).offset(params.offset)))
    return Page(items=items, total=total, limit=params.limit, offset=params.offset)
