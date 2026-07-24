from app.core.config import settings


def test_login_with_seeded_admin_returns_token(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": settings.initial_admin_email, "password": settings.initial_admin_password},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_me_endpoint_requires_valid_token(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_login_then_me_returns_current_user(client):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": settings.initial_admin_email, "password": settings.initial_admin_password},
    )
    token = login_response.json()["access_token"]

    me_response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200
    assert me_response.json()["email"] == settings.initial_admin_email
