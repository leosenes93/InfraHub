import enum
import uuid

from sqlalchemy import ARRAY, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TimestampedModel


class AssetType(enum.StrEnum):
    """Categorias de ativos de infraestrutura suportadas pelo inventário."""

    SERVER = "server"
    VIRTUAL_MACHINE = "virtual_machine"
    NETWORK_DEVICE = "network_device"
    CONTAINER = "container"
    APPLICATION = "application"


class AssetStatus(enum.StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


def _enum_values(enum_cls: type[enum.StrEnum]) -> list[str]:
    return [member.value for member in enum_cls]


class Asset(TimestampedModel):
    __tablename__ = "assets"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type", native_enum=True, values_callable=_enum_values),
        index=True,
        nullable=False,
    )
    status: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus, name="asset_status", native_enum=True, values_callable=_enum_values),
        default=AssetStatus.ACTIVE,
        nullable=False,
    )
    environment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    documentation: Mapped[str | None] = mapped_column(Text, nullable=True)
