from app.core.config import settings


def _login(client, email: str, password: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _admin_token(client) -> str:
    return _login(client, settings.initial_admin_email, settings.initial_admin_password)


def _create_user(client, admin_token: str, email: str, role: str) -> None:
    response = client.post(
        "/api/v1/users",
        json={"email": email, "full_name": "Teste", "role": role, "password": "senha12345"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201, response.text


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_asset(client, token: str, name: str) -> str:
    response = client.post(
        "/api/v1/assets",
        json={
            "name": name,
            "asset_type": "server",
            "attributes": {"hostname": name},
        },
        headers=_auth_headers(token),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_upload_list_and_download_attachment(client):
    token = _admin_token(client)
    asset_id = _create_asset(client, token, "srv-with-attachment")

    upload_response = client.post(
        f"/api/v1/assets/{asset_id}/attachments",
        files={"file": ("diagrama.txt", b"conteudo do diagrama", "text/plain")},
        headers=_auth_headers(token),
    )
    assert upload_response.status_code == 201, upload_response.text
    attachment = upload_response.json()
    assert attachment["filename"] == "diagrama.txt"
    assert attachment["size_bytes"] == len(b"conteudo do diagrama")

    list_response = client.get(
        f"/api/v1/assets/{asset_id}/attachments", headers=_auth_headers(token)
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    download_response = client.get(
        f"/api/v1/assets/{asset_id}/attachments/{attachment['id']}/download",
        headers=_auth_headers(token),
    )
    assert download_response.status_code == 200
    assert download_response.content == b"conteudo do diagrama"


def test_delete_attachment_as_admin(client):
    token = _admin_token(client)
    asset_id = _create_asset(client, token, "srv-delete-attachment")

    upload_response = client.post(
        f"/api/v1/assets/{asset_id}/attachments",
        files={"file": ("nota.txt", b"nota", "text/plain")},
        headers=_auth_headers(token),
    )
    attachment_id = upload_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/assets/{asset_id}/attachments/{attachment_id}", headers=_auth_headers(token)
    )
    assert delete_response.status_code == 204

    list_response = client.get(
        f"/api/v1/assets/{asset_id}/attachments", headers=_auth_headers(token)
    )
    assert list_response.json() == []


def test_upload_rejects_unsupported_content_type(client):
    token = _admin_token(client)
    asset_id = _create_asset(client, token, "srv-bad-content-type")

    response = client.post(
        f"/api/v1/assets/{asset_id}/attachments",
        files={"file": ("script.exe", b"MZ", "application/x-msdownload")},
        headers=_auth_headers(token),
    )
    assert response.status_code == 415


def test_upload_rejects_file_too_large(client, monkeypatch):
    monkeypatch.setattr(settings, "max_upload_size_mb", 0)
    token = _admin_token(client)
    asset_id = _create_asset(client, token, "srv-too-large")

    response = client.post(
        f"/api/v1/assets/{asset_id}/attachments",
        files={"file": ("grande.txt", b"conteudo maior que zero MB", "text/plain")},
        headers=_auth_headers(token),
    )
    assert response.status_code == 413


def test_viewer_cannot_upload_attachment(client):
    admin_token = _admin_token(client)
    asset_id = _create_asset(client, admin_token, "srv-viewer-upload")
    _create_user(client, admin_token, "viewer.attachments@infrahub.io", "viewer")
    viewer_token = _login(client, "viewer.attachments@infrahub.io", "senha12345")

    response = client.post(
        f"/api/v1/assets/{asset_id}/attachments",
        files={"file": ("proibido.txt", b"nao deveria subir", "text/plain")},
        headers=_auth_headers(viewer_token),
    )
    assert response.status_code == 403


def test_operator_cannot_delete_attachment(client):
    admin_token = _admin_token(client)
    asset_id = _create_asset(client, admin_token, "srv-operator-delete")
    _create_user(client, admin_token, "operator.attachments@infrahub.io", "operator")
    operator_token = _login(client, "operator.attachments@infrahub.io", "senha12345")

    upload_response = client.post(
        f"/api/v1/assets/{asset_id}/attachments",
        files={"file": ("nota.txt", b"nota do operador", "text/plain")},
        headers=_auth_headers(operator_token),
    )
    assert upload_response.status_code == 201
    attachment_id = upload_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/assets/{asset_id}/attachments/{attachment_id}",
        headers=_auth_headers(operator_token),
    )
    assert delete_response.status_code == 403
