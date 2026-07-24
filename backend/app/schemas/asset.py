import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.asset import AssetStatus, AssetType


class ServerAttributes(BaseModel):
    hostname: str
    ip_address: str | None = None
    os: str | None = None
    cpu_cores: int | None = None
    ram_gb: int | None = None
    disk_gb: int | None = None


class VirtualMachineAttributes(BaseModel):
    hostname: str
    ip_address: str | None = None
    hypervisor: str | None = None
    host_server: str | None = None
    vcpu: int | None = None
    ram_gb: int | None = None
    disk_gb: int | None = None


class NetworkDeviceAttributes(BaseModel):
    device_type: Literal["switch", "router", "firewall", "access_point", "load_balancer"]
    ip_address: str | None = None
    vendor: str | None = None
    model: str | None = None
    firmware_version: str | None = None


class ContainerAttributes(BaseModel):
    image: str
    ports: list[str] = Field(default_factory=list)
    host_server: str | None = None
    orchestrator: str | None = None


class ApplicationAttributes(BaseModel):
    repository_url: str | None = None
    version: str | None = None
    language: str | None = None
    deployment_url: str | None = None


_ATTRIBUTES_SCHEMA_BY_TYPE: dict[AssetType, type[BaseModel]] = {
    AssetType.SERVER: ServerAttributes,
    AssetType.VIRTUAL_MACHINE: VirtualMachineAttributes,
    AssetType.NETWORK_DEVICE: NetworkDeviceAttributes,
    AssetType.CONTAINER: ContainerAttributes,
    AssetType.APPLICATION: ApplicationAttributes,
}


class AssetBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    asset_type: AssetType
    status: AssetStatus = AssetStatus.ACTIVE
    environment: str | None = Field(default=None, max_length=50)
    description: str | None = None
    location: str | None = Field(default=None, max_length=255)
    tags: list[str] = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)
    documentation: str | None = None

    @model_validator(mode="after")
    def validate_attributes_for_type(self) -> "AssetBase":
        schema_cls = _ATTRIBUTES_SCHEMA_BY_TYPE[self.asset_type]
        validated = schema_cls.model_validate(self.attributes)
        self.attributes = validated.model_dump()
        return self


class AssetCreate(AssetBase):
    pass


class AssetUpdate(AssetBase):
    pass


class AssetRead(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class AssetTypeCount(BaseModel):
    asset_type: AssetType
    count: int


class AssetStatusCount(BaseModel):
    status: AssetStatus
    count: int


class AssetSummary(BaseModel):
    total: int
    by_type: list[AssetTypeCount]
    by_status: list[AssetStatusCount]
