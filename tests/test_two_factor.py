import pyotp
from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "tfa@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 800001,
    "last_name": "Tfa",
    "first_name": "Test",
}


def _register_and_token(client: TestClient) -> str:
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    return client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    ).json()["access_token"]


def _enable_2fa(client: TestClient, token: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    secret = client.post("/api/v1/auth/2fa/setup", headers=headers).json()["secret"]
    code = pyotp.TOTP(secret).now()
    client.post("/api/v1/auth/2fa/enable", headers=headers, json={"otp_code": code})
    return secret


def test_setup_returns_secret_and_uri(client: TestClient) -> None:
    token = _register_and_token(client)

    response = client.post(
        "/api/v1/auth/2fa/setup", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["secret"]
    assert body["provisioning_uri"].startswith("otpauth://")


def test_enable_with_valid_code(client: TestClient) -> None:
    token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    secret = client.post("/api/v1/auth/2fa/setup", headers=headers).json()["secret"]

    response = client.post(
        "/api/v1/auth/2fa/enable",
        headers=headers,
        json={"otp_code": pyotp.TOTP(secret).now()},
    )

    assert response.status_code == 204


def test_enable_with_invalid_code_rejected(client: TestClient) -> None:
    token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/v1/auth/2fa/setup", headers=headers)

    response = client.post(
        "/api/v1/auth/2fa/enable", headers=headers, json={"otp_code": "000000"}
    )

    assert response.status_code == 400


def test_login_requires_code_when_enabled(client: TestClient) -> None:
    token = _register_and_token(client)
    _enable_2fa(client, token)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )

    assert response.status_code == 401


def test_login_succeeds_with_valid_code(client: TestClient) -> None:
    token = _register_and_token(client)
    secret = _enable_2fa(client, token)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
            "otp_code": pyotp.TOTP(secret).now(),
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_fails_with_invalid_code(client: TestClient) -> None:
    token = _register_and_token(client)
    _enable_2fa(client, token)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
            "otp_code": "000000",
        },
    )

    assert response.status_code == 401


def test_disable_removes_2fa(client: TestClient) -> None:
    token = _register_and_token(client)
    _enable_2fa(client, token)

    client.post(
        "/api/v1/auth/2fa/disable", headers={"Authorization": f"Bearer {token}"}
    )
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )

    assert response.status_code == 200
