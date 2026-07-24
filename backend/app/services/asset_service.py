import uuid

from sqlalchemy.orm import Session

from app.core.storage import delete_asset_upload_dir
from app.models.asset import Asset, AssetStatus, AssetType
from app.repositories.asset_repository import AssetRepository
from app.schemas.asset import (
    AssetCreate,
    AssetStatusCount,
    AssetSummary,
    AssetTypeCount,
    AssetUpdate,
)
from app.services.exceptions import (
    AssetAlreadyLinkedToZabbixError,
    AssetMissingIpAddressError,
    AssetNotFoundError,
)


class AssetService:
    def __init__(self, db: Session) -> None:
        self.repository = AssetRepository(db)

    def list_assets(
        self,
        asset_type: AssetType | None = None,
        status: AssetStatus | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Asset]:
        return self.repository.list_filtered(
            asset_type=asset_type, status=status, search=search, skip=skip, limit=limit
        )

    def get_asset(self, asset_id: uuid.UUID) -> Asset:
        asset = self.repository.get(asset_id)
        if asset is None:
            raise AssetNotFoundError(f"Ativo {asset_id} nao encontrado")
        return asset

    def create_asset(self, data: AssetCreate, owner_id: uuid.UUID | None) -> Asset:
        asset = Asset(
            name=data.name,
            asset_type=data.asset_type,
            status=data.status,
            environment=data.environment,
            description=data.description,
            location=data.location,
            tags=data.tags,
            attributes=data.attributes,
            documentation=data.documentation,
            zabbix_host_id=data.zabbix_host_id,
            owner_id=owner_id,
        )
        return self.repository.add(asset)

    def update_asset(self, asset_id: uuid.UUID, data: AssetUpdate) -> Asset:
        asset = self.get_asset(asset_id)
        asset.name = data.name
        asset.asset_type = data.asset_type
        asset.status = data.status
        asset.environment = data.environment
        asset.description = data.description
        asset.location = data.location
        asset.tags = data.tags
        asset.attributes = data.attributes
        asset.documentation = data.documentation
        asset.zabbix_host_id = data.zabbix_host_id
        return self.repository.update(asset)

    def set_zabbix_host_id(self, asset_id: uuid.UUID, zabbix_host_id: str) -> Asset:
        asset = self.get_asset(asset_id)
        asset.zabbix_host_id = zabbix_host_id
        return self.repository.update(asset)

    def require_zabbix_linkable(self, asset: Asset) -> str:
        if asset.zabbix_host_id:
            raise AssetAlreadyLinkedToZabbixError("Ativo ja esta vinculado a um host do Zabbix")

        ip_address = asset.attributes.get("ip_address")
        if not ip_address:
            raise AssetMissingIpAddressError("Ativo nao possui endereco IP cadastrado")
        return ip_address

    def delete_asset(self, asset_id: uuid.UUID) -> None:
        asset = self.get_asset(asset_id)
        self.repository.delete(asset)
        delete_asset_upload_dir(asset_id)

    def search_assets(self, query: str, limit: int = 20) -> list[Asset]:
        return self.repository.search(query, limit=limit)

    def get_summary(self) -> AssetSummary:
        return AssetSummary(
            total=self.repository.count_total(),
            by_type=[
                AssetTypeCount(asset_type=t, count=c) for t, c in self.repository.count_by_type()
            ],
            by_status=[
                AssetStatusCount(status=s, count=c) for s, c in self.repository.count_by_status()
            ],
        )
