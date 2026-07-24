from pydantic import BaseModel

from app.schemas.asset import AssetRead


class SearchResponse(BaseModel):
    query: str
    results: list[AssetRead]
