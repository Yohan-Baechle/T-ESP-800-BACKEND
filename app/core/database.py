from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Classe de base déclarative dont héritent tous les modèles ORM."""


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI fournissant une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
