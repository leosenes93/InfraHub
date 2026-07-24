import logging
from datetime import datetime

from docker.errors import DockerException

from app.core.docker_client import get_docker_client
from app.schemas.docker import DockerContainerRead
from app.services.exceptions import DockerUnavailableError

logger = logging.getLogger(__name__)


class DockerService:
    def list_containers(self) -> list[DockerContainerRead]:
        try:
            client = get_docker_client()
            containers = client.containers.list(all=True)
        except DockerException as exc:
            logger.warning("docker_unavailable", extra={"error": str(exc)})
            raise DockerUnavailableError("Nao foi possivel conectar ao socket do Docker") from exc

        return [self._to_schema(container) for container in containers]

    @staticmethod
    def _to_schema(container) -> DockerContainerRead:
        try:
            image_tags = container.image.tags
            image = image_tags[0] if image_tags else container.image.short_id
        except DockerException:
            image = "desconhecida"

        ports: list[str] = []
        for container_port, bindings in (container.ports or {}).items():
            if not bindings:
                ports.append(container_port)
                continue
            for binding in bindings:
                ports.append(f"{binding['HostIp']}:{binding['HostPort']}->{container_port}")

        created_raw = container.attrs.get("Created")
        created_at = (
            datetime.fromisoformat(created_raw.replace("Z", "+00:00")) if created_raw else None
        )

        return DockerContainerRead(
            id=container.short_id,
            name=container.name,
            image=image,
            status=container.status,
            state=container.attrs.get("State", {}).get("Status", container.status),
            created_at=created_at,
            ports=ports,
        )
