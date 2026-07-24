import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.models.asset import Asset, AssetStatus, AssetType
from app.models.user import User, UserRole
from app.schemas.asset import AssetCreate, AssetRead, AssetSummary, AssetUpdate
from app.services.asset_service import AssetService
from app.services.exceptions import AssetNotFoundError

router = APIRouter(prefix="/assets", tags=["assets"])

_can_write = require_roles(UserRole.ADMIN, UserRole.ANALYST, UserRole.OPERATOR)
_can_delete = require_roles(UserRole.ADMIN)


@router.get("", response_model=list[AssetRead], dependencies=[Depends(get_current_user)])
def list_assets(
    asset_type: AssetType | None = None,
    status_filter: AssetStatus | None = Query(default=None, alias="status"),
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
) -> list[Asset]:
    return AssetService(db).list_assets(
        asset_type=asset_type, status=status_filter, search=search, skip=skip, limit=limit
    )


@router.get("/summary", response_model=AssetSummary, dependencies=[Depends(get_current_user)])
def get_assets_summary(db: Session = Depends(get_db_session)) -> AssetSummary:
    return AssetService(db).get_summary()


@router.get("/{asset_id}", response_model=AssetRead, dependencies=[Depends(get_current_user)])
def get_asset(asset_id: uuid.UUID, db: Session = Depends(get_db_session)) -> Asset:
    try:
        return AssetService(db).get_asset(asset_id)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "",
    response_model=AssetRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_can_write)],
)
def create_asset(
    data: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> Asset:
    return AssetService(db).create_asset(data, owner_id=current_user.id)


@router.patch(
    "/{asset_id}",
    response_model=AssetRead,
    dependencies=[Depends(_can_write)],
)
def update_asset(
    asset_id: uuid.UUID, data: AssetUpdate, db: Session = Depends(get_db_session)
) -> Asset:
    try:
        return AssetService(db).update_asset(asset_id, data)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(_can_delete)],
)
def delete_asset(asset_id: uuid.UUID, db: Session = Depends(get_db_session)) -> None:
    try:
        AssetService(db).delete_asset(asset_id)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
