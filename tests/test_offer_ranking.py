from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "rank@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 151515,
    "last_name": "Rank",
    "first_name": "Cab",
}

NANCY = {"latitude": 48.69, "longitude": 6.18}
PARIS = {"latitude": 48.85, "longitude": 2.35}


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


def _located_office(
    client: TestClient, headers: dict[str, str], coords: dict[str, float]
) -> str:
    office_id = client.post(
        "/api/v1/nursing-offices",
        headers=headers,
        json={"nursing_office_name": "Cabinet"},
    ).json()["nursing_office_id"]
    client.put(
        f"/api/v1/nursing-offices/{office_id}/contact-info",
        headers=headers,
        json=coords,
    )
    return office_id


def _offer(
    client: TestClient, headers: dict[str, str], office_id: str, turnover: str
) -> str:
    return client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "nursing_office_id": office_id,
            "start": "2026-09-01T08:00:00Z",
            "end": "2026-09-10T18:00:00Z",
            "estimated_turnover": turnover,
        },
    ).json()["offer_id"]


def test_geo_search_orders_by_distance(client: TestClient) -> None:
    headers = _auth_headers(client)
    nancy = _located_office(client, headers, NANCY)
    paris = _located_office(client, headers, PARIS)
    nancy_offer = _offer(client, headers, nancy, "2000")
    paris_offer = _offer(client, headers, paris, "9000")

    response = client.get(
        "/api/v1/offers?near_lat=48.69&near_lon=6.18&radius_km=500", headers=headers
    )

    ids = [o["offer_id"] for o in response.json()["items"]]
    assert ids.index(nancy_offer) < ids.index(paris_offer)


def test_without_geo_orders_by_turnover_desc(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _located_office(client, headers, NANCY)
    low = _offer(client, headers, office_id, "2000")
    high = _offer(client, headers, office_id, "9000")

    response = client.get("/api/v1/offers", headers=headers)

    ids = [o["offer_id"] for o in response.json()["items"]]
    assert ids.index(high) < ids.index(low)
