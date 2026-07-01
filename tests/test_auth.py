from fastapi.testclient import TestClient

VALID_PAYLOAD = {
    "email": "marie.durand@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 123456,
    "last_name": "Durand",
    "first_name": "Marie",
    "replacement_nurse": True,
}


def test_register_returns_created_nurse(client: TestClient) -> None:
    response = client.post("/api/v1/auth/register", json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == VALID_PAYLOAD["email"]
    assert body["status"] == "pending"
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_duplicate_email_conflicts(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json=VALID_PAYLOAD)

    response = client.post("/api/v1/auth/register", json=VALID_PAYLOAD)

    assert response.status_code == 409


def test_login_returns_bearer_token(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json=VALID_PAYLOAD)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["password"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_unauthorized(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json=VALID_PAYLOAD)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": VALID_PAYLOAD["email"], "password": "MauvaisMotDePasse"},
    )

    assert response.status_code == 401
