from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "care@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 141414,
    "last_name": "Care",
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


def _create_care(client: TestClient, headers: dict[str, str], name: str) -> str:
    return client.post(
        "/api/v1/cares", headers=headers, json={"care_name": name}
    ).json()["care_id"]


def _office(client: TestClient, headers: dict[str, str]) -> str:
    return client.post(
        "/api/v1/nursing-offices",
        headers=headers,
        json={"nursing_office_name": "Cabinet"},
    ).json()["nursing_office_id"]


def test_create_and_list_cares(client: TestClient) -> None:
    headers = _auth_headers(client)
    _create_care(client, headers, "Pansement")

    response = client.get("/api/v1/cares", headers=headers)

    assert response.status_code == 200
    assert any(c["care_name"] == "Pansement" for c in response.json())


def test_duplicate_care_conflicts(client: TestClient) -> None:
    headers = _auth_headers(client)
    _create_care(client, headers, "Injection")

    response = client.post(
        "/api/v1/cares", headers=headers, json={"care_name": "Injection"}
    )

    assert response.status_code == 409


def test_publish_offer_with_care(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _office(client, headers)
    care_id = _create_care(client, headers, "Pansement")

    response = client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "nursing_office_id": office_id,
            "start": "2026-09-01T08:00:00Z",
            "end": "2026-09-10T18:00:00Z",
            "care_ids": [care_id],
        },
    )

    assert response.status_code == 201


def test_filter_offers_by_care(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _office(client, headers)
    pansement = _create_care(client, headers, "Pansement")
    injection = _create_care(client, headers, "Injection")
    client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "nursing_office_id": office_id,
            "start": "2026-09-01T08:00:00Z",
            "end": "2026-09-10T18:00:00Z",
            "care_ids": [pansement],
        },
    )

    with_pansement = client.get(
        f"/api/v1/offers?care_id={pansement}&nursing_office_id={office_id}",
        headers=headers,
    )
    with_injection = client.get(
        f"/api/v1/offers?care_id={injection}&nursing_office_id={office_id}",
        headers=headers,
    )

    assert len(with_pansement.json()) == 1
    assert with_injection.json() == []


def test_publish_offer_with_unknown_care_rejected(client: TestClient) -> None:
    headers = _auth_headers(client)
    office_id = _office(client, headers)

    response = client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "nursing_office_id": office_id,
            "start": "2026-09-01T08:00:00Z",
            "end": "2026-09-10T18:00:00Z",
            "care_ids": ["00000000-0000-0000-0000-000000000000"],
        },
    )

    assert response.status_code == 422
