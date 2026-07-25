import httpx
import pytest

from app.services import kubernetes_service as kube_module
from app.services.exceptions import DockerUnavailableError
from app.services.kubernetes_service import KubernetesService, is_running_in_kubernetes


def test_is_running_in_kubernetes_false_when_token_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(kube_module, "_TOKEN_PATH", tmp_path / "token")
    assert is_running_in_kubernetes() is False


def test_is_running_in_kubernetes_true_when_token_present(tmp_path, monkeypatch):
    token_path = tmp_path / "token"
    token_path.write_text("fake-token")
    monkeypatch.setattr(kube_module, "_TOKEN_PATH", token_path)
    assert is_running_in_kubernetes() is True


def _sa_files(tmp_path, monkeypatch):
    token_path = tmp_path / "token"
    ca_path = tmp_path / "ca.crt"
    namespace_path = tmp_path / "namespace"
    token_path.write_text("fake-token")
    ca_path.write_text("fake-ca")
    namespace_path.write_text("infrahub")
    monkeypatch.setattr(kube_module, "_TOKEN_PATH", token_path)
    monkeypatch.setattr(kube_module, "_CA_CERT_PATH", ca_path)
    monkeypatch.setattr(kube_module, "_NAMESPACE_PATH", namespace_path)


def test_list_containers_maps_pods_to_schema(tmp_path, monkeypatch):
    _sa_files(tmp_path, monkeypatch)

    pods_payload = {
        "items": [
            {
                "metadata": {
                    "uid": "pod-uid-1",
                    "name": "infrahub-backend-abc",
                    "creationTimestamp": "2026-01-01T00:00:00Z",
                },
                "spec": {
                    "containers": [
                        {
                            "image": "infrahub-backend:prod",
                            "ports": [{"containerPort": 8000, "protocol": "TCP"}],
                        }
                    ]
                },
                "status": {"phase": "Running"},
            }
        ]
    }

    def _fake_get(url, headers, verify, timeout):
        assert "infrahub" in url
        assert headers["Authorization"] == "Bearer fake-token"
        return httpx.Response(200, json=pods_payload, request=httpx.Request("GET", url))

    monkeypatch.setattr(kube_module.httpx, "get", _fake_get)

    result = KubernetesService().list_containers()

    assert len(result) == 1
    pod = result[0]
    assert pod.id == "pod-uid-1"
    assert pod.name == "infrahub-backend-abc"
    assert pod.image == "infrahub-backend:prod"
    assert pod.status == "Running"
    assert pod.state == "running"
    assert pod.ports == ["8000/TCP"]
    assert pod.created_at is not None


def test_list_containers_raises_when_api_unavailable(tmp_path, monkeypatch):
    _sa_files(tmp_path, monkeypatch)

    def _fake_get(url, headers, verify, timeout):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(kube_module.httpx, "get", _fake_get)

    with pytest.raises(DockerUnavailableError):
        KubernetesService().list_containers()
