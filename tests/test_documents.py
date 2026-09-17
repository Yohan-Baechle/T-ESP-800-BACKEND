import io

from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "doc@infirmo.fr",
    "password": "MotDePasse1",
    "order_number": 112233,
    "last_name": "Doc",
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


def _pdf(size: int = 32) -> bytes:
    return b"%PDF-1.4" + b"0" * (size - 8)


def test_upload_pdf_returns_created_document(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.post(
        "/api/v1/documents",
        headers=headers,
        data={"document_type": "professional_card"},
        files={"file": ("carte.pdf", io.BytesIO(_pdf()), "application/pdf")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["document_type"] == "professional_card"
    assert body["status"] == "pending"


def test_upload_rejects_non_pdf(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.post(
        "/api/v1/documents",
        headers=headers,
        data={"document_type": "rib"},
        files={"file": ("note.txt", io.BytesIO(b"plain"), "text/plain")},
    )

    assert response.status_code == 415


def test_upload_rejects_oversized_file(client: TestClient) -> None:
    headers = _auth_headers(client)

    response = client.post(
        "/api/v1/documents",
        headers=headers,
        data={"document_type": "insurance"},
        files={
            "file": ("big.pdf", io.BytesIO(_pdf(6 * 1024 * 1024)), "application/pdf")
        },
    )

    assert response.status_code == 413


def test_upload_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/api/v1/documents",
        data={"document_type": "rib"},
        files={"file": ("carte.pdf", io.BytesIO(_pdf()), "application/pdf")},
    )

    assert response.status_code == 401


def test_list_returns_only_own_documents(client: TestClient) -> None:
    headers = _auth_headers(client)
    client.post(
        "/api/v1/documents",
        headers=headers,
        data={"document_type": "rib"},
        files={"file": ("rib.pdf", io.BytesIO(_pdf()), "application/pdf")},
    )

    response = client.get("/api/v1/documents", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
