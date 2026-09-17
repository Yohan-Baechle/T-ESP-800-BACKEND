from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "search@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 990011,
    "last_name": "Search",
    "first_name": "Cab",
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


def _office(client: TestClient, headers: dict[str, str]) -> str:
    return client.post(
        "/api/v1/nursing-offices",
        headers=headers,
        json={"nursing_office_name": "Cabinet"},
    ).json()["nursing_office_id"]


def _offer(
    client: TestClient,
    headers: dict[str, str],
    office_id: str,
    turnover: str,
    start: str = "2026-09-01T08:00:00Z",
    end: str = "2026-09-10T18:00:00Z",
) -> None:
    client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "nursing_office_id": office_id,
            "start": start,
            "end": end,
            "estimated_turnover": turnover,
        },
    )


def test_filter_by_min_turnover(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _office(client, headers)
    _offer(client, headers, office_id, "2000")
    _offer(client, headers, office_id, "4000")
    _offer(client, headers, office_id, "6000")

    response = client.get("/api/v1/offers?min_turnover=3500", headers=headers)

    assert response.status_code == 200
    assert response.json()["total"] == 2


def test_filter_by_office(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _office(client, headers)
    _offer(client, headers, office_id, "2000")

    response = client.get(
        f"/api/v1/offers?nursing_office_id={office_id}", headers=headers
    )

    assert response.json()["total"] == 1


def test_filter_by_start_after_excludes_earlier(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _office(client, headers)
    _offer(client, headers, office_id, "2000")

    response = client.get(
        "/api/v1/offers?start_after=2026-10-01T00:00:00Z", headers=headers
    )

    assert response.json()["items"] == []


def test_negative_turnover_rejected(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.get("/api/v1/offers?min_turnover=-1", headers=headers)

    assert response.status_code == 422
