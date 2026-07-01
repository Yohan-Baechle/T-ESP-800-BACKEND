from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.database import Base, get_db
from app.main import app

settings = get_settings()

TEST_DB_NAME = "infirmo_test"
_admin_url = settings.database_url.rsplit("/", 1)[0]
TEST_DATABASE_URL = f"{_admin_url}/{TEST_DB_NAME}"


@pytest.fixture(scope="session", autouse=True)
def _test_database() -> Generator[None, None, None]:
    """Crée une base de test dédiée pour toute la session, puis la supprime."""
    admin = create_engine(f"{_admin_url}/postgres", isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin.dispose()

    yield

    admin = create_engine(f"{_admin_url}/postgres", isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)'))
    admin.dispose()


@pytest.fixture(scope="session")
def _engine(_test_database: None):
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(_engine) -> Generator[Session, None, None]:
    """Session isolée : schéma recréé puis supprimé à chaque test."""
    Base.metadata.create_all(_engine)
    session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(_engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
