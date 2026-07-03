from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "audit@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 400001,
    "last_name": "Audit",
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


def test_requests_are_logged(client: TestClient) -> None:
    headers = _auth_headers(client)
    client.get("/api/v1/patients", headers=headers)

    logs = client.get("/api/v1/admin/audit-logs", headers=headers).json()

    assert any(entry["action"] == "http.request" for entry in logs)


def test_transmission_creation_is_audited(client: TestClient) -> None:
    headers = _auth_headers(client)
    patient_id = client.post(
        "/api/v1/patients",
        headers=headers,
        json={"last_name": "Dupont", "first_name": "Jean"},
    ).json()["patient_id"]
    client.post(
        f"/api/v1/patients/{patient_id}/transmissions",
        headers=headers,
        json={"text": "Note"},
    )

    logs = client.get("/api/v1/admin/audit-logs", headers=headers).json()

    assert any(entry["action"] == "transmission.created" for entry in logs)


def test_anonymization_is_audited(client: TestClient) -> None:
    headers = _auth_headers(client)
    patient_id = client.post(
        "/api/v1/patients",
        headers=headers,
        json={"last_name": "Dupont", "first_name": "Jean"},
    ).json()["patient_id"]
    client.delete(f"/api/v1/patients/{patient_id}", headers=headers)

    logs = client.get("/api/v1/admin/audit-logs", headers=headers).json()

    assert any(entry["action"] == "patient.anonymized" for entry in logs)


def test_audit_logs_require_auth(client: TestClient) -> None:
    assert client.get("/api/v1/admin/audit-logs").status_code == 401
