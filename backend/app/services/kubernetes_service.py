import logging
from datetime import datetime
from pathlib import Path

import httpx

from app.schemas.docker import DockerContainerRead
from app.services.exceptions import DockerUnavailableError

logger = logging.getLogger(__name__)

_SA_DIR = Path("/var/run/secrets/kubernetes.io/serviceaccount")
_TOKEN_PATH = _SA_DIR / "token"
_CA_CERT_PATH = _SA_DIR / "ca.crt"
_NAMESPACE_PATH = _SA_DIR / "namespace"


def is_running_in_kubernetes() -> bool:
    return _TOKEN_PATH.exists()


class KubernetesService:
    """Alternativa ao DockerService quando o backend roda dentro de um Pod —
    nao ha socket do Docker para conectar, mas a propria API do Kubernetes
    (acessivel via o token da ServiceAccount montado no Pod) da uma visao
    equivalente dos workloads em execucao no namespace do InfraHub."""

    def list_containers(self) -> list[DockerContainerRead]:
        namespace = _NAMESPACE_PATH.read_text().strip()
        token = _TOKEN_PATH.read_text().strip()

        try:
            response = httpx.get(
                f"https://kubernetes.default.svc/api/v1/namespaces/{namespace}/pods",
                headers={"Authorization": f"Bearer {token}"},
                verify=str(_CA_CERT_PATH),
                timeout=5.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("kubernetes_unavailable", extra={"error": str(exc)})
            raise DockerUnavailableError("Nao foi possivel consultar a API do Kubernetes") from exc

        pods = response.json().get("items", [])
        return [self._to_schema(pod) for pod in pods]

    @staticmethod
    def _to_schema(pod: dict) -> DockerContainerRead:
        metadata = pod.get("metadata", {})
        spec = pod.get("spec", {})
        status = pod.get("status", {})
        containers = spec.get("containers", [])

        image = containers[0]["image"] if containers else "desconhecida"

        ports: list[str] = []
        for container in containers:
            for port in container.get("ports", []):
                proto = port.get("protocol", "TCP")
                ports.append(f"{port['containerPort']}/{proto}")

        phase = status.get("phase", "Unknown")
        created_raw = metadata.get("creationTimestamp")
        created_at = (
            datetime.fromisoformat(created_raw.replace("Z", "+00:00")) if created_raw else None
        )

        return DockerContainerRead(
            id=metadata.get("uid", metadata.get("name", "")),
            name=metadata.get("name", ""),
            image=image,
            status=phase,
            state=phase.lower(),
            created_at=created_at,
            ports=ports,
        )
