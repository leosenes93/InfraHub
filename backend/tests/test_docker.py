from app.api.v1 import docker as docker_route
from app.core.config import settings
from app.schemas.docker import DockerContainerRead
from app.services.exceptions import DockerUnavailableError


def _force_docker_env(monkeypatch):
    monkeypatch.setattr(docker_route, "is_running_in_kubernetes", lambda: False)


def _login(client, email: str, password: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _admin_token(client) -> str:
    return _login(client, settings.initial_admin_email, settings.initial_admin_password)


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_list_containers_returns_mocked_data(client, monkeypatch):
    _force_docker_env(monkeypatch)
    sample = DockerContainerRead(
        id="abc123",
        name="infrahub-backend-1",
        image="infrahub-backend:latest",
        status="running",
        state="running",
        created_at=None,
        ports=["0.0.0.0:8000->8000/tcp"],
    )
    monkeypatch.setattr(
        docker_route.DockerService, "list_containers", lambda self: [sample]
    )

    token = _admin_token(client)
    response = client.get("/api/v1/docker/containers", headers=_auth_headers(token))

    assert response.status_code == 200
    assert response.json() == [sample.model_dump(mode="json")]


def test_list_containers_returns_503_when_docker_unavailable(client, monkeypatch):
    _force_docker_env(monkeypatch)

    def _raise(self):
        raise DockerUnavailableError("Nao foi possivel conectar ao socket do Docker")

    monkeypatch.setattr(docker_route.DockerService, "list_containers", _raise)

    token = _admin_token(client)
    response = client.get("/api/v1/docker/containers", headers=_auth_headers(token))

    assert response.status_code == 503


def test_list_containers_requires_authentication(client):
    response = client.get("/api/v1/docker/containers")
    assert response.status_code == 401


def test_list_containers_uses_kubernetes_service_when_in_cluster(client, monkeypatch):
    sample = DockerContainerRead(
        id="pod-uid-1",
        name="infrahub-backend-abc",
        image="infrahub-backend:prod",
        status="Running",
        state="running",
        created_at=None,
        ports=["8000/TCP"],
    )
    monkeypatch.setattr(docker_route, "is_running_in_kubernetes", lambda: True)
    monkeypatch.setattr(
        docker_route.KubernetesService, "list_containers", lambda self: [sample]
    )

    token = _admin_token(client)
    response = client.get("/api/v1/docker/containers", headers=_auth_headers(token))

    assert response.status_code == 200
    assert response.json() == [sample.model_dump(mode="json")]
