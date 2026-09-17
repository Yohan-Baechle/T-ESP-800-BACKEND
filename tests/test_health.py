from collections.abc import Generator

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app


def test_liveness_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_reports_database_up(client: TestClient) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["database"] == "up"


def test_readiness_reports_database_down(client: TestClient) -> None:
    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise RuntimeError("database unreachable")

    def override_broken_db() -> Generator[BrokenSession, None, None]:
        yield BrokenSession()

    app.dependency_overrides[get_db] = override_broken_db
    try:
        response = client.get("/health/ready")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json()["database"] == "down"


def test_health_is_public(client: TestClient) -> None:
    assert client.get("/health").status_code == 200
