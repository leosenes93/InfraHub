from datetime import datetime

from pydantic import BaseModel


class ZabbixProblem(BaseModel):
    name: str
    severity: str
    since: datetime


class AssetMonitoringStatus(BaseModel):
    linked: bool
    zabbix_host_id: str | None = None
    host_name: str | None = None
    available: bool | None = None
    problems: list[ZabbixProblem] = []
