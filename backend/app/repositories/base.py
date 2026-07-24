import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import Base


class BaseRepository[ModelType: Base]:
    """Encapsula o acesso a dados de uma entidade, sem regras de negocio."""

    model: type[ModelType]

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, entity_id: uuid.UUID) -> ModelType | None:
        return self.db.get(self.model, entity_id)

    def list(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return list(self.db.scalars(select(self.model).offset(skip).limit(limit)))

    def add(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: ModelType) -> ModelType:
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.db.delete(entity)
        self.db.commit()
