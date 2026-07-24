from app.core.config import settings


def _login(client, email: str, password: str):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def _admin_token(client) -> str:
    response = _login(client, settings.initial_admin_email, settings.initial_admin_password)
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _create_user(client, admin_token: str, email: str, role: str) -> None:
    response = client.post(
        "/api/v1/users",
        json={"email": email, "full_name": "Teste", "role": role, "password": "senha12345"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201, response.text


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_asset_crud_creates_audit_entries(client):
    token = _admin_token(client)

    create_response = client.post(
        "/api/v1/assets",
        json={
            "name": "srv-audit-demo",
            "asset_type": "server",
            "attributes": {"hostname": "srv-audit-demo"},
        },
        headers=_auth_headers(token),
    )
    asset_id = create_response.json()["id"]

    client.patch(
        f"/api/v1/assets/{asset_id}",
        json={
            "name": "srv-audit-demo",
            "asset_type": "server",
            "attributes": {"hostname": "srv-audit-demo"},
            "status": "maintenance",
        },
        headers=_auth_headers(token),
    )
    client.delete(f"/api/v1/assets/{asset_id}", headers=_auth_headers(token))

    logs_response = client.get(
        "/api/v1/audit-logs",
        params={"resource_type": "asset"},
        headers=_auth_headers(token),
    )
    assert logs_response.status_code == 200
    actions = {
        entry["action"] for entry in logs_response.json() if entry["resource_id"] == asset_id
    }
    assert {"asset.created", "asset.updated", "asset.deleted"} <= actions


def test_login_success_and_failure_create_audit_entries(client):
    admin_token = _admin_token(client)

    failed_response = _login(client, settings.initial_admin_email, "senha-errada")
    assert failed_response.status_code == 401

    logs_response = client.get(
        "/api/v1/audit-logs",
        params={"action": "auth.login_failed"},
        headers=_auth_headers(admin_token),
    )
    assert logs_response.status_code == 200
    assert any(
        entry["user_email"] == settings.initial_admin_email for entry in logs_response.json()
    )

    succeeded_response = client.get(
        "/api/v1/audit-logs",
        params={"action": "auth.login_succeeded"},
        headers=_auth_headers(admin_token),
    )
    assert len(succeeded_response.json()) >= 1


def test_viewer_cannot_list_audit_logs(client):
    admin_token = _admin_token(client)
    _create_user(client, admin_token, "viewer.audit@infrahub.io", "viewer")
    login_response = _login(client, "viewer.audit@infrahub.io", "senha12345")
    viewer_token = login_response.json()["access_token"]

    response = client.get("/api/v1/audit-logs", headers=_auth_headers(viewer_token))
    assert response.status_code == 403
