from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "offre@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 778899,
    "last_name": "Off",
    "first_name": "Cab",
}

VALID_OFFER = {
    "start": "2026-08-01T08:00:00Z",
    "end": "2026-08-15T18:00:00Z",
    "estimated_turnover": "3500.00",
    "description": "Tournée été",
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


def _create_office(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/nursing-offices",
        headers=headers,
        json={"nursing_office_name": "Cabinet Offre"},
    )
    return response.json()["nursing_office_id"]


def test_publish_offer_for_own_office(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _create_office(client, headers)

    response = client.post(
        "/api/v1/offers",
        headers=headers,
        json={"nursing_office_id": office_id, **VALID_OFFER},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "open"
    assert body["description"] == "Tournée été"


def test_list_returns_open_offers(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _create_office(client, headers)
    client.post(
        "/api/v1/offers",
        headers=headers,
        json={"nursing_office_id": office_id, **VALID_OFFER},
    )

    response = client.get("/api/v1/offers", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_publish_for_foreign_office_forbidden(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "nursing_office_id": "00000000-0000-0000-0000-000000000000",
            **VALID_OFFER,
        },
    )

    assert response.status_code == 403


def test_publish_with_end_before_start_rejected(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _create_office(client, headers)

    response = client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "nursing_office_id": office_id,
            "start": "2026-08-15T08:00:00Z",
            "end": "2026-08-01T08:00:00Z",
        },
    )

    assert response.status_code == 422


def test_publish_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/api/v1/offers",
        json={
            "nursing_office_id": "00000000-0000-0000-0000-000000000000",
            **VALID_OFFER,
        },
    )

    assert response.status_code == 401
