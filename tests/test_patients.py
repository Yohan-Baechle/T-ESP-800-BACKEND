from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.patient import Transmission

REGISTER_PAYLOAD = {
    "email": "nurse@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 300001,
    "last_name": "Nurse",
    "first_name": "Test",
}

PATIENT_PAYLOAD = {
    "last_name": "Dupont",
    "first_name": "Jean",
    "birth_date": "1950-03-15",
    "note": "Diabétique",
}


def _auth_headers(client: TestClient) -> dict[str, str]:
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_patient(client: TestClient, headers: dict[str, str]) -> str:
    return client.post(
        "/api/v1/patients", headers=headers, json=PATIENT_PAYLOAD
    ).json()["patient_id"]


def test_create_patient(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.post("/api/v1/patients", headers=headers, json=PATIENT_PAYLOAD)

    assert response.status_code == 201
    assert response.json()["status"] == "active"


def test_create_transmission_sets_expiry(client: TestClient) -> None:
    headers = _auth_headers(client)
    patient_id = _create_patient(client, headers)

    response = client.post(
        f"/api/v1/patients/{patient_id}/transmissions",
        headers=headers,
        json={"text": "Pansement refait"},
    )

    assert response.status_code == 201
    body = response.json()
    created = datetime.fromisoformat(body["created_at"])
    expires = datetime.fromisoformat(body["expires_at"])
    assert 29 <= (expires - created).days <= 30


def test_list_transmissions_returns_active(client: TestClient) -> None:
    headers = _auth_headers(client)
    patient_id = _create_patient(client, headers)
    client.post(
        f"/api/v1/patients/{patient_id}/transmissions",
        headers=headers,
        json={"text": "Note"},
    )

    response = client.get(
        f"/api/v1/patients/{patient_id}/transmissions", headers=headers
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_expired_transmission_is_hidden(
    client: TestClient, db_session: Session
) -> None:
    headers = _auth_headers(client)
    patient_id = _create_patient(client, headers)
    client.post(
        f"/api/v1/patients/{patient_id}/transmissions",
        headers=headers,
        json={"text": "Ancienne transmission"},
    )
    db_session.execute(
        update(Transmission).values(expires_at=datetime.now(UTC) - timedelta(days=1))
    )
    db_session.commit()

    response = client.get(
        f"/api/v1/patients/{patient_id}/transmissions", headers=headers
    )

    assert response.json()["items"] == []


def test_anonymize_patient_removes_data(client: TestClient) -> None:
    headers = _auth_headers(client)
    patient_id = _create_patient(client, headers)

    delete = client.delete(f"/api/v1/patients/{patient_id}", headers=headers)

    assert delete.status_code == 204
    listing = client.get("/api/v1/patients", headers=headers)
    assert all(p["patient_id"] != patient_id for p in listing.json()["items"])


def test_anonymized_patient_not_accessible(client: TestClient) -> None:
    headers = _auth_headers(client)
    patient_id = _create_patient(client, headers)
    client.delete(f"/api/v1/patients/{patient_id}", headers=headers)

    response = client.get(
        f"/api/v1/patients/{patient_id}/transmissions", headers=headers
    )

    assert response.status_code == 404


def test_patients_require_auth(client: TestClient) -> None:
    assert client.get("/api/v1/patients").status_code == 401
