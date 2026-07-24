import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.storage import build_storage_path
from app.models.attachment import AssetAttachment
from app.repositories.attachment_repository import AttachmentRepository
from app.services.exceptions import (
    AttachmentNotFoundError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)

ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/svg+xml",
    "application/pdf",
    "text/markdown",
    "text/plain",
}


class AttachmentService:
    def __init__(self, db: Session) -> None:
        self.repository = AttachmentRepository(db)

    def list_attachments(self, asset_id: uuid.UUID) -> list[AssetAttachment]:
        return self.repository.list_by_asset(asset_id)

    def get_attachment(self, asset_id: uuid.UUID, attachment_id: uuid.UUID) -> AssetAttachment:
        attachment = self.repository.get_for_asset(asset_id, attachment_id)
        if attachment is None:
            raise AttachmentNotFoundError(f"Anexo {attachment_id} nao encontrado")
        return attachment

    def save_upload(
        self, asset_id: uuid.UUID, upload_file: UploadFile, uploaded_by_id: uuid.UUID | None
    ) -> AssetAttachment:
        content_type = upload_file.content_type or "application/octet-stream"
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise UnsupportedFileTypeError(f"Tipo de arquivo nao suportado: {content_type}")

        content = upload_file.file.read()
        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise FileTooLargeError(f"Arquivo excede o limite de {settings.max_upload_size_mb}MB")

        filename = upload_file.filename or "arquivo"
        storage_path = build_storage_path(asset_id, filename)
        storage_path.write_bytes(content)

        attachment = AssetAttachment(
            asset_id=asset_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
            storage_path=str(storage_path),
            uploaded_by_id=uploaded_by_id,
        )
        return self.repository.add(attachment)

    def delete_attachment(self, asset_id: uuid.UUID, attachment_id: uuid.UUID) -> None:
        attachment = self.get_attachment(asset_id, attachment_id)
        Path(attachment.storage_path).unlink(missing_ok=True)
        self.repository.delete(attachment)
