import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.models.attachment import AssetAttachment
from app.models.user import User, UserRole
from app.schemas.attachment import AttachmentRead
from app.services.asset_service import AssetService
from app.services.attachment_service import AttachmentService
from app.services.audit_service import record_audit_event
from app.services.exceptions import (
    AssetNotFoundError,
    AttachmentNotFoundError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)

router = APIRouter(prefix="/assets/{asset_id}/attachments", tags=["attachments"])

_can_write = require_roles(UserRole.ADMIN, UserRole.ANALYST, UserRole.OPERATOR)
_can_delete = require_roles(UserRole.ADMIN)


def _ensure_asset_exists(asset_id: uuid.UUID, db: Session) -> None:
    try:
        AssetService(db).get_asset(asset_id)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[AttachmentRead], dependencies=[Depends(get_current_user)])
def list_attachments(
    asset_id: uuid.UUID, db: Session = Depends(get_db_session)
) -> list[AssetAttachment]:
    _ensure_asset_exists(asset_id, db)
    return AttachmentService(db).list_attachments(asset_id)


@router.post(
    "",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_can_write)],
)
def upload_attachment(
    asset_id: uuid.UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AssetAttachment:
    _ensure_asset_exists(asset_id, db)
    try:
        attachment = AttachmentService(db).save_upload(
            asset_id, file, uploaded_by_id=current_user.id
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exc)
        ) from exc
    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=str(exc)
        ) from exc

    record_audit_event(
        db,
        action="attachment.uploaded",
        actor=current_user,
        resource_type="asset",
        resource_id=asset_id,
        details={"filename": attachment.filename, "attachment_id": str(attachment.id)},
    )
    return attachment


@router.get("/{attachment_id}/download", dependencies=[Depends(get_current_user)])
def download_attachment(
    asset_id: uuid.UUID, attachment_id: uuid.UUID, db: Session = Depends(get_db_session)
) -> FileResponse:
    _ensure_asset_exists(asset_id, db)
    try:
        attachment = AttachmentService(db).get_attachment(asset_id, attachment_id)
    except AttachmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return FileResponse(
        path=attachment.storage_path,
        media_type=attachment.content_type,
        filename=attachment.filename,
    )


@router.delete(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(_can_delete)],
)
def delete_attachment(
    asset_id: uuid.UUID,
    attachment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> None:
    _ensure_asset_exists(asset_id, db)
    try:
        attachment = AttachmentService(db).get_attachment(asset_id, attachment_id)
        AttachmentService(db).delete_attachment(asset_id, attachment_id)
    except AttachmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    record_audit_event(
        db,
        action="attachment.deleted",
        actor=current_user,
        resource_type="asset",
        resource_id=asset_id,
        details={"filename": attachment.filename, "attachment_id": str(attachment_id)},
    )
