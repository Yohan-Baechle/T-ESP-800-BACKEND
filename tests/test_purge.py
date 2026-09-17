from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.patient import Transmission

REGISTER_PAYLOAD = {
    "email": "purge@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 600001,
    "last_name": "Purge",
    "first_name": "Test",
}


def _admin_headers(client: TestClient, promote_to_admin) -> dict[str, str]:
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    promote_to_admin(REGISTER_PAYLOAD["email"])
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _patient_with_transmission(
    client: TestClient, headers: dict[str, str]
) -> tuple[str, str]:
    patient_id = client.post(
        "/api/v1/patients",
        headers=headers,
        json={"last_name": "Dupont", "first_name": "Jean"},
    ).json()["patient_id"]
    transmission_id = client.post(
        f"/api/v1/patients/{patient_id}/transmissions",
        headers=headers,
        json={"text": "Note"},
    ).json()["transmission_id"]
    return patient_id, transmission_id


def test_purge_removes_expired(
    client: TestClient, db_session: Session, promote_to_admin
) -> None:
    headers = _admin_headers(client, promote_to_admin)
    _, transmission_id = _patient_with_transmission(client, headers)
    db_session.execute(
        update(Transmission).values(expires_at=datetime.now(UTC) - timedelta(days=1))
    )
    db_session.commit()

    response = client.post("/api/v1/admin/purge-transmissions", headers=headers)

    assert response.status_code == 200
    assert response.json()["deleted"] == 1
    remaining = db_session.scalars(select(Transmission)).all()
    assert all(t.transmission_id != transmission_id for t in remaining)


def test_purge_keeps_valid(
    client: TestClient, db_session: Session, promote_to_admin
) -> None:
    headers = _admin_headers(client, promote_to_admin)
    _patient_with_transmission(client, headers)

    response = client.post("/api/v1/admin/purge-transmissions", headers=headers)

    assert response.json()["deleted"] == 0
    assert len(db_session.scalars(select(Transmission)).all()) == 1


def test_purge_requires_auth(client: TestClient) -> None:
    assert client.post("/api/v1/admin/purge-transmissions").status_code == 401


def test_purge_forbidden_for_non_admin(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    token = client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    ).json()["access_token"]

    response = client.post(
        "/api/v1/admin/purge-transmissions",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
