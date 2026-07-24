from app.core.config import settings


def _admin_token(client) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": settings.initial_admin_email, "password": settings.initial_admin_password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_search_finds_asset_by_name_substring(client):
    token = _admin_token(client)
    client.post(
        "/api/v1/assets",
        json={
            "name": "srv-search-alpha",
            "asset_type": "server",
            "attributes": {"hostname": "srv-search-alpha"},
        },
        headers=_auth_headers(token),
    )
    client.post(
        "/api/v1/assets",
        json={
            "name": "app-unrelated",
            "asset_type": "application",
            "attributes": {},
        },
        headers=_auth_headers(token),
    )

    response = client.get(
        "/api/v1/search", params={"q": "search-alpha"}, headers=_auth_headers(token)
    )
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "search-alpha"
    names = {item["name"] for item in body["results"]}
    assert "srv-search-alpha" in names
    assert "app-unrelated" not in names


def test_search_requires_authentication(client):
    response = client.get("/api/v1/search", params={"q": "srv"})
    assert response.status_code == 401
