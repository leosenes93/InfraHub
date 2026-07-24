import uuid

from sqlalchemy import select

from app.models.attachment import AssetAttachment
from app.repositories.base import BaseRepository


class AttachmentRepository(BaseRepository[AssetAttachment]):
    model = AssetAttachment

    def list_by_asset(self, asset_id: uuid.UUID) -> list[AssetAttachment]:
        stmt = (
            select(AssetAttachment)
            .where(AssetAttachment.asset_id == asset_id)
            .order_by(AssetAttachment.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def get_for_asset(
        self, asset_id: uuid.UUID, attachment_id: uuid.UUID
    ) -> AssetAttachment | None:
        stmt = select(AssetAttachment).where(
            AssetAttachment.id == attachment_id, AssetAttachment.asset_id == asset_id
        )
        return self.db.scalar(stmt)
