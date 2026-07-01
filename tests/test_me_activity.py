from fastapi.testclient import TestClient


def _register_and_login(
    client: TestClient, email: str, order_number: int
) -> dict[str, str]:
    payload = {
        "email": email,
        "password": "MotDePasse1",
        "order_number": order_number,
        "last_name": "Nom",
        "first_name": "Prenom",
    }
    client.post("/api/v1/auth/register", json=payload)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "MotDePasse1"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_open_offer(client: TestClient, headers: dict[str, str]) -> str:
    office = client.post(
        "/api/v1/nursing-offices",
        headers=headers,
        json={"nursing_office_name": "Cabinet"},
    ).json()["nursing_office_id"]
    return client.post(
        "/api/v1/offers",
        headers=headers,
        json={
            "nursing_office_id": office,
            "start": "2026-08-01T08:00:00Z",
            "end": "2026-08-15T18:00:00Z",
        },
    ).json()["offer_id"]


def test_my_applications_lists_own(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    replacer = _register_and_login(client, "rep@i.fr", 100002)
    offer_id = _create_open_offer(client, cabinet)
    client.post(f"/api/v1/offers/{offer_id}/apply", headers=replacer, json={})

    response = client.get("/api/v1/me/applications", headers=replacer)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_my_applications_empty_for_new_user(client: TestClient) -> None:
    replacer = _register_and_login(client, "rep@i.fr", 100002)

    response = client.get("/api/v1/me/applications", headers=replacer)

    assert response.status_code == 200
    assert response.json() == []


def test_my_offers_lists_office_offers(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    _create_open_offer(client, cabinet)

    response = client.get("/api/v1/me/offers", headers=cabinet)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_my_offers_empty_without_office(client: TestClient) -> None:
    replacer = _register_and_login(client, "rep@i.fr", 100002)

    response = client.get("/api/v1/me/offers", headers=replacer)

    assert response.status_code == 200
    assert response.json() == []


def test_my_activity_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/me/applications").status_code == 401
    assert client.get("/api/v1/me/offers").status_code == 401
