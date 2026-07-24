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


def test_create_and_get_server_asset(client):
    token = _admin_token(client)

    response = client.post(
        "/api/v1/assets",
        json={
            "name": "srv-web-01",
            "asset_type": "server",
            "status": "active",
            "environment": "production",
            "attributes": {"hostname": "srv-web-01", "cpu_cores": 8, "ram_gb": 32},
        },
        headers=_auth_headers(token),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "srv-web-01"
    assert body["attributes"]["hostname"] == "srv-web-01"

    get_response = client.get(f"/api/v1/assets/{body['id']}", headers=_auth_headers(token))
    assert get_response.status_code == 200
    assert get_response.json()["id"] == body["id"]


def test_create_asset_rejects_attributes_for_wrong_type(client):
    token = _admin_token(client)

    response = client.post(
        "/api/v1/assets",
        json={
            "name": "switch-core-01",
            "asset_type": "network_device",
            "attributes": {"hostname": "not-a-network-device-field"},
        },
        headers=_auth_headers(token),
    )
    assert response.status_code == 422


def test_list_assets_filters_by_type(client):
    token = _admin_token(client)
    client.post(
        "/api/v1/assets",
        json={
            "name": "app-billing",
            "asset_type": "application",
            "attributes": {"repository_url": "https://example.com/billing", "version": "1.0.0"},
        },
        headers=_auth_headers(token),
    )

    response = client.get(
        "/api/v1/assets", params={"asset_type": "application"}, headers=_auth_headers(token)
    )
    assert response.status_code == 200
    assert all(item["asset_type"] == "application" for item in response.json())


def test_assets_summary_reflects_created_assets(client):
    token = _admin_token(client)
    client.post(
        "/api/v1/assets",
        json={
            "name": "vm-app-01",
            "asset_type": "virtual_machine",
            "attributes": {"hostname": "vm-app-01"},
        },
        headers=_auth_headers(token),
    )

    response = client.get("/api/v1/assets/summary", headers=_auth_headers(token))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(item["count"] > 0 for item in body["by_type"])


def test_update_and_delete_asset_as_admin(client):
    token = _admin_token(client)
    create_response = client.post(
        "/api/v1/assets",
        json={
            "name": "container-temp",
            "asset_type": "container",
            "attributes": {"image": "nginx:alpine"},
        },
        headers=_auth_headers(token),
    )
    asset_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/assets/{asset_id}",
        json={
            "name": "container-temp",
            "asset_type": "container",
            "status": "maintenance",
            "attributes": {"image": "nginx:latest"},
        },
        headers=_auth_headers(token),
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "maintenance"

    delete_response = client.delete(f"/api/v1/assets/{asset_id}", headers=_auth_headers(token))
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/assets/{asset_id}", headers=_auth_headers(token))
    assert get_response.status_code == 404


def test_viewer_cannot_create_asset(client):
    admin_token = _admin_token(client)
    _create_user(client, admin_token, "viewer.assets@infrahub.io", "viewer")
    viewer_token = _login(client, "viewer.assets@infrahub.io", "senha12345")

    response = client.post(
        "/api/v1/assets",
        json={
            "name": "srv-forbidden",
            "asset_type": "server",
            "attributes": {"hostname": "srv-forbidden"},
        },
        headers=_auth_headers(viewer_token),
    )
    assert response.status_code == 403


def test_operator_cannot_delete_asset(client):
    admin_token = _admin_token(client)
    _create_user(client, admin_token, "operator.assets@infrahub.io", "operator")
    operator_token = _login(client, "operator.assets@infrahub.io", "senha12345")

    create_response = client.post(
        "/api/v1/assets",
        json={
            "name": "srv-operator-owned",
            "asset_type": "server",
            "attributes": {"hostname": "srv-operator-owned"},
        },
        headers=_auth_headers(operator_token),
    )
    assert create_response.status_code == 201
    asset_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/assets/{asset_id}", headers=_auth_headers(operator_token)
    )
    assert delete_response.status_code == 403
