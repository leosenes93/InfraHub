from sqlalchemy import func, or_, select

from app.models.asset import Asset, AssetStatus, AssetType
from app.repositories.base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    model = Asset

    def list_filtered(
        self,
        asset_type: AssetType | None = None,
        status: AssetStatus | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Asset]:
        stmt = select(Asset)
        if asset_type is not None:
            stmt = stmt.where(Asset.asset_type == asset_type)
        if status is not None:
            stmt = stmt.where(Asset.status == status)
        if search:
            stmt = stmt.where(Asset.name.ilike(f"%{search}%"))
        stmt = stmt.order_by(Asset.name).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def count_by_type(self) -> list[tuple[AssetType, int]]:
        stmt = select(Asset.asset_type, func.count()).group_by(Asset.asset_type)
        return list(self.db.execute(stmt).all())

    def count_by_status(self) -> list[tuple[AssetStatus, int]]:
        stmt = select(Asset.status, func.count()).group_by(Asset.status)
        return list(self.db.execute(stmt).all())

    def count_total(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Asset)) or 0

    def search(self, query: str, limit: int = 20) -> list[Asset]:
        name_similarity = func.similarity(Asset.name, query)
        description_similarity = func.similarity(func.coalesce(Asset.description, ""), query)
        relevance = func.greatest(name_similarity, description_similarity)

        stmt = (
            select(Asset)
            .where(
                or_(
                    Asset.name.ilike(f"%{query}%"),
                    Asset.description.ilike(f"%{query}%"),
                    name_similarity > 0.2,
                    description_similarity > 0.2,
                )
            )
            .order_by(relevance.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))
