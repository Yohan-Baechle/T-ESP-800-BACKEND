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


def _me_id(client: TestClient, headers: dict[str, str]) -> str:
    return client.get("/api/v1/profils/me", headers=headers).json()["user_id"]


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


def test_apply_to_offer(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    replacer = _register_and_login(client, "rep@i.fr", 100002)
    offer_id = _create_open_offer(client, cabinet)

    response = client.post(
        f"/api/v1/offers/{offer_id}/apply",
        headers=replacer,
        json={"application_message": "Motivé"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "submitted"
    assert body["decision"] == "pending"


def test_cannot_apply_twice(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    replacer = _register_and_login(client, "rep@i.fr", 100002)
    offer_id = _create_open_offer(client, cabinet)

    client.post(f"/api/v1/offers/{offer_id}/apply", headers=replacer, json={})
    response = client.post(
        f"/api/v1/offers/{offer_id}/apply", headers=replacer, json={}
    )

    assert response.status_code == 409


def test_cannot_apply_to_own_offer(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    offer_id = _create_open_offer(client, cabinet)

    response = client.post(f"/api/v1/offers/{offer_id}/apply", headers=cabinet, json={})

    assert response.status_code == 403


def test_office_lists_applications(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    replacer = _register_and_login(client, "rep@i.fr", 100002)
    offer_id = _create_open_offer(client, cabinet)
    client.post(f"/api/v1/offers/{offer_id}/apply", headers=replacer, json={})

    response = client.get(f"/api/v1/offers/{offer_id}/applications", headers=cabinet)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_non_member_cannot_list_applications(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    replacer = _register_and_login(client, "rep@i.fr", 100002)
    offer_id = _create_open_offer(client, cabinet)
    client.post(f"/api/v1/offers/{offer_id}/apply", headers=replacer, json={})

    response = client.get(f"/api/v1/offers/{offer_id}/applications", headers=replacer)

    assert response.status_code == 403


def test_office_accepts_application(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    replacer = _register_and_login(client, "rep@i.fr", 100002)
    replacer_id = _me_id(client, replacer)
    offer_id = _create_open_offer(client, cabinet)
    client.post(f"/api/v1/offers/{offer_id}/apply", headers=replacer, json={})

    response = client.patch(
        f"/api/v1/offers/{offer_id}/applications/{replacer_id}",
        headers=cabinet,
        json={"decision": "accepted", "decision_comment": "Bienvenue"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "accepted"
    assert body["status"] == "reviewed"


def test_acceptance_closes_offer(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    replacer = _register_and_login(client, "rep@i.fr", 100002)
    replacer_id = _me_id(client, replacer)
    offer_id = _create_open_offer(client, cabinet)
    client.post(f"/api/v1/offers/{offer_id}/apply", headers=replacer, json={})

    client.patch(
        f"/api/v1/offers/{offer_id}/applications/{replacer_id}",
        headers=cabinet,
        json={"decision": "accepted"},
    )

    open_offers = client.get("/api/v1/offers", headers=replacer).json()
    assert all(o["offer_id"] != offer_id for o in open_offers)


def test_acceptance_rejects_other_applications(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    first = _register_and_login(client, "first@i.fr", 100002)
    second = _register_and_login(client, "second@i.fr", 100003)
    first_id = _me_id(client, first)
    offer_id = _create_open_offer(client, cabinet)
    client.post(f"/api/v1/offers/{offer_id}/apply", headers=first, json={})
    client.post(f"/api/v1/offers/{offer_id}/apply", headers=second, json={})

    client.patch(
        f"/api/v1/offers/{offer_id}/applications/{first_id}",
        headers=cabinet,
        json={"decision": "accepted"},
    )

    applications = client.get(
        f"/api/v1/offers/{offer_id}/applications", headers=cabinet
    ).json()
    decisions = {app["user_id"]: app["decision"] for app in applications}
    assert decisions[first_id] == "accepted"
    other = next(uid for uid in decisions if uid != first_id)
    assert decisions[other] == "rejected"


def test_cannot_apply_to_closed_offer(client: TestClient) -> None:
    cabinet = _register_and_login(client, "cab@i.fr", 100001)
    first = _register_and_login(client, "first@i.fr", 100002)
    first_id = _me_id(client, first)
    offer_id = _create_open_offer(client, cabinet)
    client.post(f"/api/v1/offers/{offer_id}/apply", headers=first, json={})
    client.patch(
        f"/api/v1/offers/{offer_id}/applications/{first_id}",
        headers=cabinet,
        json={"decision": "accepted"},
    )

    late = _register_and_login(client, "late@i.fr", 100004)
    response = client.post(f"/api/v1/offers/{offer_id}/apply", headers=late, json={})

    assert response.status_code == 409
