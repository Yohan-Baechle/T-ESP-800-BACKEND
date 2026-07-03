from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.encryption import decrypt, encrypt

REGISTER_PAYLOAD = {
    "email": "enc@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 500001,
    "last_name": "Enc",
    "first_name": "Test",
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


def test_encrypt_decrypt_roundtrip() -> None:
    ciphertext = encrypt("Donnée sensible")

    assert ciphertext != "Donnée sensible"
    assert decrypt(ciphertext) == "Donnée sensible"


def test_encrypt_uses_random_nonce() -> None:
    assert encrypt("même texte") != encrypt("même texte")


def test_transmission_text_is_encrypted_at_rest(
    client: TestClient, db_session: Session
) -> None:
    headers = _auth_headers(client)
    patient_id = client.post(
        "/api/v1/patients",
        headers=headers,
        json={"last_name": "Dupont", "first_name": "Jean"},
    ).json()["patient_id"]
    secret = "PANSEMENT_CONFIDENTIEL_42"
    client.post(
        f"/api/v1/patients/{patient_id}/transmissions",
        headers=headers,
        json={"text": secret},
    )

    stored = db_session.execute(text("SELECT text FROM transmission")).scalar()

    assert secret not in stored
    assert decrypt(stored) == secret


def test_transmission_text_readable_through_api(client: TestClient) -> None:
    headers = _auth_headers(client)
    patient_id = client.post(
        "/api/v1/patients",
        headers=headers,
        json={"last_name": "Dupont", "first_name": "Jean"},
    ).json()["patient_id"]
    client.post(
        f"/api/v1/patients/{patient_id}/transmissions",
        headers=headers,
        json={"text": "Lisible via API"},
    )

    response = client.get(
        f"/api/v1/patients/{patient_id}/transmissions", headers=headers
    )

    assert response.json()[0]["text"] == "Lisible via API"
