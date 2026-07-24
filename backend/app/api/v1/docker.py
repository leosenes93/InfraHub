from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.schemas.docker import DockerContainerRead
from app.services.docker_service import DockerService
from app.services.exceptions import DockerUnavailableError

router = APIRouter(prefix="/docker", tags=["docker"])


@router.get(
    "/containers",
    response_model=list[DockerContainerRead],
    dependencies=[Depends(get_current_user)],
)
def list_containers() -> list[DockerContainerRead]:
    try:
        return DockerService().list_containers()
    except DockerUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
