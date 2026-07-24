import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.models.user import User, UserRole
from app.schemas.monitoring import AssetMonitoringStatus
from app.services.asset_service import AssetService
from app.services.audit_service import record_audit_event
from app.services.exceptions import (
    AssetAlreadyLinkedToZabbixError,
    AssetMissingIpAddressError,
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

_can_link = require_roles(UserRole.ADMIN, UserRole.ANALYST, UserRole.OPERATOR)


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


@router.post(
    "/link-zabbix",
    response_model=AssetMonitoringStatus,
    dependencies=[Depends(_can_link)],
)
def link_asset_to_zabbix(
    asset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AssetMonitoringStatus:
    asset_service = AssetService(db)
    try:
        asset = asset_service.get_asset(asset_id)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    try:
        ip_address = asset_service.require_zabbix_linkable(asset)
    except AssetAlreadyLinkedToZabbixError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except AssetMissingIpAddressError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc

    try:
        zabbix_host_id = ZabbixService().create_host(asset.name, ip_address)
    except (ZabbixNotConfiguredError, ZabbixUnavailableError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    asset_service.set_zabbix_host_id(asset_id, zabbix_host_id)
    record_audit_event(
        db,
        action="asset.zabbix_linked",
        actor=current_user,
        resource_type="asset",
        resource_id=asset.id,
        details={"name": asset.name, "zabbix_host_id": zabbix_host_id},
    )

    status_data = ZabbixService().get_host_status(zabbix_host_id)
    return AssetMonitoringStatus(
        linked=True,
        zabbix_host_id=zabbix_host_id,
        host_name=status_data["host_name"],
        available=status_data["available"],
        problems=status_data["problems"],
    )
