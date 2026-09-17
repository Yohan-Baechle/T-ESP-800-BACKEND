from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "cabinet@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 445566,
    "last_name": "Cab",
    "first_name": "Titulaire",
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


def test_create_nursing_office(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.post(
        "/api/v1/nursing-offices",
        headers=headers,
        json={"nursing_office_name": "Cabinet du Centre", "siret": 12345678900011},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["nursing_office_name"] == "Cabinet du Centre"
    assert body["status"] == "active"


def test_list_returns_linked_offices(client: TestClient) -> None:
    headers = _auth_headers(client)
    client.post(
        "/api/v1/nursing-offices",
        headers=headers,
        json={"nursing_office_name": "Cabinet A"},
    )

    response = client.get("/api/v1/nursing-offices", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nursing_office_name"] == "Cabinet A"


def test_create_requires_auth(client: TestClient) -> None:
    response = client.post("/api/v1/nursing-offices", json={"nursing_office_name": "X"})

    assert response.status_code == 401
