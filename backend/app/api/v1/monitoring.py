import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.schemas.monitoring import AssetMonitoringStatus
from app.services.asset_service import AssetService
from app.services.exceptions import (
    AssetNotFoundError,
    ZabbixNotConfiguredError,
    ZabbixUnavailableError,
)
from app.services.zabbix_service import ZabbixService

router = APIRouter(
    prefix="/assets/{asset_id}/monitoring",
    tags=["monitoring"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=AssetMonitoringStatus)
def get_asset_monitoring(
    asset_id: uuid.UUID, db: Session = Depends(get_db_session)
) -> AssetMonitoringStatus:
    try:
        asset = AssetService(db).get_asset(asset_id)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if not asset.zabbix_host_id:
        return AssetMonitoringStatus(linked=False)

    try:
        status_data = ZabbixService().get_host_status(asset.zabbix_host_id)
    except (ZabbixNotConfiguredError, ZabbixUnavailableError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    return AssetMonitoringStatus(
        linked=True,
        zabbix_host_id=asset.zabbix_host_id,
        host_name=status_data["host_name"],
        available=status_data["available"],
        problems=status_data["problems"],
    )
