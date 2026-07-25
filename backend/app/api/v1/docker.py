from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.schemas.docker import DockerContainerRead
from app.services.docker_service import DockerService
from app.services.exceptions import DockerUnavailableError
from app.services.kubernetes_service import KubernetesService, is_running_in_kubernetes

router = APIRouter(prefix="/docker", tags=["docker"])


@router.get(
    "/containers",
    response_model=list[DockerContainerRead],
    dependencies=[Depends(get_current_user)],
)
def list_containers() -> list[DockerContainerRead]:
    # O backend roda tanto via Docker Compose (com o socket do Docker montado)
    # quanto dentro de um Pod (Kubernetes/OpenShift/k3s), onde nao ha socket
    # nenhum para conectar — nesse caso, a API do Kubernetes da a visao
    # equivalente dos workloads em execucao no namespace do InfraHub.
    service = KubernetesService() if is_running_in_kubernetes() else DockerService()
    try:
        return service.list_containers()
    except DockerUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
