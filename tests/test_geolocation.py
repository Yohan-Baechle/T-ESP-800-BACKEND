from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "geo@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 121212,
    "last_name": "Geo",
    "first_name": "Cab",
}

NANCY = {"latitude": 48.6921, "longitude": 6.1844}


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


def _office_with_location(client: TestClient, headers: dict[str, str]) -> str:
    office_id = client.post(
        "/api/v1/nursing-offices",
        headers=headers,
        json={"nursing_office_name": "Cabinet Nancy"},
    ).json()["nursing_office_id"]
    client.put(
        f"/api/v1/nursing-offices/{office_id}/contact-info",
        headers=headers,
        json={"city": "Nancy", **NANCY},
    )
    return office_id


def _publish_offer(client: TestClient, headers: dict[str, str], office_id: str) -> None:
    client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "nursing_office_id": office_id,
            "start": "2026-09-01T08:00:00Z",
            "end": "2026-09-10T18:00:00Z",
        },
    )


def test_upsert_contact_info_returns_coordinates(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = client.post(
        "/api/v1/nursing-offices",
        headers=headers,
        json={"nursing_office_name": "Cabinet"},
    ).json()["nursing_office_id"]

    response = client.put(
        f"/api/v1/nursing-offices/{office_id}/contact-info",
        headers=headers,
        json={"city": "Nancy", **NANCY},
    )

    assert response.status_code == 200
    body = response.json()
    assert round(body["latitude"], 4) == NANCY["latitude"]
    assert round(body["longitude"], 4) == NANCY["longitude"]


def test_search_within_radius_finds_offer(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _office_with_location(client, headers)
    _publish_offer(client, headers, office_id)

    response = client.get(
        f"/api/v1/offers?near_lat=48.69&near_lon=6.18&radius_km=10"
        f"&nursing_office_id={office_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_outside_radius_excludes_offer(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _office_with_location(client, headers)
    _publish_offer(client, headers, office_id)

    response = client.get(
        f"/api/v1/offers?near_lat=48.85&near_lon=2.35&radius_km=10"
        f"&nursing_office_id={office_id}",
        headers=headers,
    )

    assert response.json() == []


def test_incomplete_geo_params_rejected(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.get("/api/v1/offers?near_lat=48.69", headers=headers)

    assert response.status_code == 422


def test_contact_info_requires_membership(client: TestClient) -> None:
    _auth_headers(client)
    other = client.post(
        "/api/v1/auth/register",
        json={**REGISTER_PAYLOAD, "email": "other@i.fr", "order_number": 131313},
    )
    assert other.status_code == 201
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "other@i.fr", "password": "MotDePasse1"},
    ).json()["access_token"]

    response = client.put(
        "/api/v1/nursing-offices/00000000-0000-0000-0000-000000000000/contact-info",
        headers={"Authorization": f"Bearer {token}"},
        json={"city": "X", **NANCY},
    )

    assert response.status_code == 403
