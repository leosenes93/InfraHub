from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.schemas.search import SearchResponse
from app.services.asset_service import AssetService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse, dependencies=[Depends(get_current_user)])
def search(
    q: str = Query(min_length=1), db: Session = Depends(get_db_session)
) -> SearchResponse:
    # Escopo atual: busca em ativos (nome/descricao). Extensivel a outros
    # tipos de recurso (wiki, usuarios) em fases futuras.
    results = AssetService(db).search_assets(q)
    return SearchResponse(query=q, results=results)
