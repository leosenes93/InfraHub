from datetime import datetime

from pydantic import BaseModel


class DockerContainerRead(BaseModel):
    id: str
    name: str
    image: str
    status: str
    state: str
    created_at: datetime | None
    ports: list[str]
