import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    uploaded_by_id: uuid.UUID | None
    created_at: datetime
