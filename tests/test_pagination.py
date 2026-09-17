from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "page@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 700001,
    "last_name": "Page",
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


def _create_offers(client: TestClient, headers: dict[str, str], count: int) -> None:
    office_id = client.post(
        "/api/v1/nursing-offices",
        headers=headers,
        json={"nursing_office_name": "Cabinet"},
    ).json()["nursing_office_id"]
    for _ in range(count):
        client.post(
            "/api/v1/offers",
            headers=headers,
            json={
                "nursing_office_id": office_id,
                "start": "2026-09-01T08:00:00Z",
                "end": "2026-09-10T18:00:00Z",
            },
        )


def test_response_is_wrapped(client: TestClient) -> None:
    headers = _auth_headers(client)
    _create_offers(client, headers, 3)

    body = client.get("/api/v1/offers", headers=headers).json()

    assert set(body) == {"items", "total", "limit", "offset"}
    assert body["total"] == 3
    assert len(body["items"]) == 3


def test_limit_and_offset(client: TestClient) -> None:
    headers = _auth_headers(client)
    _create_offers(client, headers, 5)

    first = client.get("/api/v1/offers?limit=2&offset=0", headers=headers).json()
    second = client.get("/api/v1/offers?limit=2&offset=2", headers=headers).json()

    assert first["total"] == 5
    assert len(first["items"]) == 2
    assert len(second["items"]) == 2
    first_ids = {o["offer_id"] for o in first["items"]}
    second_ids = {o["offer_id"] for o in second["items"]}
    assert first_ids.isdisjoint(second_ids)


def test_invalid_limit_rejected(client: TestClient) -> None:
    headers = _auth_headers(client)

    assert client.get("/api/v1/offers?limit=0", headers=headers).status_code == 422
    assert client.get("/api/v1/offers?limit=101", headers=headers).status_code == 422
