from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "profil@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 654321,
    "last_name": "Ancien",
    "first_name": "Prenom",
    "replacement_nurse": False,
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


def test_get_profile_returns_current_nurse(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.get("/api/v1/profils/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]


def test_patch_profile_updates_fields(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.patch(
        "/api/v1/profils/me",
        headers=headers,
        json={"last_name": "Nouveau", "replacement_nurse": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["last_name"] == "Nouveau"
    assert body["replacement_nurse"] is True


def test_patch_profile_is_partial(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.patch(
        "/api/v1/profils/me", headers=headers, json={"last_name": "SeulChamp"}
    )

    body = response.json()
    assert body["last_name"] == "SeulChamp"
    assert body["first_name"] == REGISTER_PAYLOAD["first_name"]


def test_patch_profile_requires_auth(client: TestClient) -> None:
    response = client.patch("/api/v1/profils/me", json={"last_name": "X"})

    assert response.status_code == 401
