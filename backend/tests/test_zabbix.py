from app.api.v1 import monitoring as monitoring_route
from app.core.config import settings
from app.services.exceptions import ZabbixUnavailableError


def _login(client, email: str, password: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _admin_token(client) -> str:
    return _login(client, settings.initial_admin_email, settings.initial_admin_password)


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_asset(client, token: str, **overrides) -> str:
    payload = {
        "name": "srv-zabbix-01",
        "asset_type": "server",
        "attributes": {"hostname": "srv-zabbix-01"},
    }
    payload.update(overrides)
    response = client.post("/api/v1/assets", json=payload, headers=_auth_headers(token))
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_monitoring_returns_unlinked_for_asset_without_zabbix_host(client):
    token = _admin_token(client)
    asset_id = _create_asset(client, token)

    response = client.get(
        f"/api/v1/assets/{asset_id}/monitoring", headers=_auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json() == {
        "linked": False,
        "zabbix_host_id": None,
        "host_name": None,
        "available": None,
        "problems": [],
    }


def test_monitoring_returns_mocked_live_status_for_linked_asset(client, monkeypatch):
    token = _admin_token(client)
    asset_id = _create_asset(client, token, zabbix_host_id="10084")

    monkeypatch.setattr(settings, "zabbix_api_token", "fake-token")
    monkeypatch.setattr(
        monitoring_route.ZabbixService,
        "get_host_status",
        lambda self, zabbix_host_id: {
            "host_name": "Zabbix server",
            "available": True,
            "problems": [],
        },
    )

    response = client.get(
        f"/api/v1/assets/{asset_id}/monitoring", headers=_auth_headers(token)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["linked"] is True
    assert body["zabbix_host_id"] == "10084"
    assert body["host_name"] == "Zabbix server"
    assert body["available"] is True


def test_monitoring_returns_503_when_zabbix_unavailable(client, monkeypatch):
    token = _admin_token(client)
    asset_id = _create_asset(client, token, zabbix_host_id="10084")

    def _raise(self, zabbix_host_id):
        raise ZabbixUnavailableError("Nao foi possivel conectar a API do Zabbix")

    monkeypatch.setattr(settings, "zabbix_api_token", "fake-token")
    monkeypatch.setattr(monitoring_route.ZabbixService, "get_host_status", _raise)

    response = client.get(
        f"/api/v1/assets/{asset_id}/monitoring", headers=_auth_headers(token)
    )

    assert response.status_code == 503


def test_monitoring_requires_authentication(client):
    response = client.get("/api/v1/assets/00000000-0000-0000-0000-000000000000/monitoring")
    assert response.status_code == 401


def test_monitoring_returns_404_for_unknown_asset(client):
    token = _admin_token(client)
    response = client.get(
        "/api/v1/assets/00000000-0000-0000-0000-000000000000/monitoring",
        headers=_auth_headers(token),
    )
    assert response.status_code == 404
