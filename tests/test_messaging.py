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


def test_open_conversation(client: TestClient) -> None:
    alice = _register_and_login(client, "alice@i.fr", 200001)
    bob = _register_and_login(client, "bob@i.fr", 200002)
    bob_id = _me_id(client, bob)

    response = client.post(
        "/api/v1/conversations", headers=alice, json={"recipient_id": bob_id}
    )

    assert response.status_code == 201


def test_open_conversation_is_idempotent(client: TestClient) -> None:
    alice = _register_and_login(client, "alice@i.fr", 200001)
    bob = _register_and_login(client, "bob@i.fr", 200002)
    alice_id = _me_id(client, alice)
    bob_id = _me_id(client, bob)

    first = client.post(
        "/api/v1/conversations", headers=alice, json={"recipient_id": bob_id}
    ).json()["conversation_id"]
    second = client.post(
        "/api/v1/conversations", headers=bob, json={"recipient_id": alice_id}
    ).json()["conversation_id"]

    assert first == second


def test_cannot_open_conversation_with_self(client: TestClient) -> None:
    alice = _register_and_login(client, "alice@i.fr", 200001)
    alice_id = _me_id(client, alice)

    response = client.post(
        "/api/v1/conversations", headers=alice, json={"recipient_id": alice_id}
    )

    assert response.status_code == 400


def test_send_and_list_messages_in_order(client: TestClient) -> None:
    alice = _register_and_login(client, "alice@i.fr", 200001)
    bob = _register_and_login(client, "bob@i.fr", 200002)
    bob_id = _me_id(client, bob)
    conv = client.post(
        "/api/v1/conversations", headers=alice, json={"recipient_id": bob_id}
    ).json()["conversation_id"]

    client.post(
        f"/api/v1/conversations/{conv}/messages",
        headers=alice,
        json={"content": "Bonjour"},
    )
    client.post(
        f"/api/v1/conversations/{conv}/messages",
        headers=bob,
        json={"content": "Salut"},
    )

    response = client.get(f"/api/v1/conversations/{conv}/messages", headers=bob)

    assert response.status_code == 200
    assert [m["content"] for m in response.json()] == ["Bonjour", "Salut"]


def test_outsider_cannot_read_conversation(client: TestClient) -> None:
    alice = _register_and_login(client, "alice@i.fr", 200001)
    bob = _register_and_login(client, "bob@i.fr", 200002)
    outsider = _register_and_login(client, "carol@i.fr", 200003)
    bob_id = _me_id(client, bob)
    conv = client.post(
        "/api/v1/conversations", headers=alice, json={"recipient_id": bob_id}
    ).json()["conversation_id"]

    response = client.get(f"/api/v1/conversations/{conv}/messages", headers=outsider)

    assert response.status_code == 403


def test_list_conversations_returns_own(client: TestClient) -> None:
    alice = _register_and_login(client, "alice@i.fr", 200001)
    bob = _register_and_login(client, "bob@i.fr", 200002)
    bob_id = _me_id(client, bob)
    client.post("/api/v1/conversations", headers=alice, json={"recipient_id": bob_id})

    response = client.get("/api/v1/conversations", headers=alice)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_messaging_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/conversations").status_code == 401
