import logging
import re
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.monitoring import ZabbixProblem
from app.services.exceptions import ZabbixNotConfiguredError, ZabbixUnavailableError

logger = logging.getLogger(__name__)

_SEVERITY_LABELS = {
    "0": "Nao classificado",
    "1": "Informacao",
    "2": "Aviso",
    "3": "Media",
    "4": "Alta",
    "5": "Desastre",
}

_HOST_GROUP_NAME = "InfraHub"
_ICMP_TEMPLATE_NAME = "ICMP Ping"
_INVALID_HOST_CHARS = re.compile(r"[^A-Za-z0-9._ -]")


class ZabbixService:
    def __init__(self) -> None:
        if not settings.zabbix_api_token:
            raise ZabbixNotConfiguredError("ZABBIX_API_TOKEN nao configurado")

    def _call(self, method: str, params: dict) -> Any:
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        headers = {
            "Content-Type": "application/json-rpc",
            "Authorization": f"Bearer {settings.zabbix_api_token}",
        }
        try:
            response = httpx.post(
                settings.zabbix_api_url, json=payload, headers=headers, timeout=5.0
            )
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            logger.warning("zabbix_unavailable", extra={"error": str(exc)})
            raise ZabbixUnavailableError("Nao foi possivel conectar a API do Zabbix") from exc

        if "error" in body:
            logger.warning("zabbix_api_error", extra={"error": body["error"]})
            detail = body["error"].get("data", body["error"])
            raise ZabbixUnavailableError(f"Erro na API do Zabbix: {detail}")

        return body["result"]

    def get_host_status(self, zabbix_host_id: str) -> dict[str, Any]:
        hosts = self._call(
            "host.get",
            {
                "output": ["hostid", "host", "status"],
                "hostids": [zabbix_host_id],
                "selectInterfaces": ["available"],
            },
        )
        if not hosts:
            return {"host_name": None, "available": None, "problems": []}

        host = hosts[0]
        available = self._resolve_availability(host.get("interfaces", []))
        problems = self._get_problems(zabbix_host_id)

        return {"host_name": host["host"], "available": available, "problems": problems}

    @staticmethod
    def _resolve_availability(interfaces: list[dict]) -> bool | None:
        if not interfaces:
            return None
        statuses = {iface["available"] for iface in interfaces}
        if "2" in statuses:
            return False
        if "1" in statuses:
            return True
        return None

    def _get_problems(self, zabbix_host_id: str) -> list[ZabbixProblem]:
        problems_raw = self._call(
            "problem.get",
            {
                "output": ["name", "severity", "clock"],
                "hostids": [zabbix_host_id],
                "sortfield": ["eventid"],
                "sortorder": "DESC",
            },
        )
        return [
            ZabbixProblem(
                name=problem["name"],
                severity=_SEVERITY_LABELS.get(problem["severity"], problem["severity"]),
                since=datetime.fromtimestamp(int(problem["clock"]), tz=UTC),
            )
            for problem in problems_raw
        ]

    def create_host(self, name: str, ip_address: str) -> str:
        group_id = self._get_or_create_host_group_id()
        template_id = self._get_icmp_template_id()
        host_name = self._sanitize_host_name(name)

        result = self._call(
            "host.create",
            {
                "host": host_name,
                "name": name,
                "groups": [{"groupid": group_id}],
                "templates": [{"templateid": template_id}],
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": ip_address,
                        "dns": "",
                        "port": "10050",
                    }
                ],
            },
        )
        return result["hostids"][0]

    def _get_or_create_host_group_id(self) -> str:
        groups = self._call("hostgroup.get", {"filter": {"name": [_HOST_GROUP_NAME]}})
        if groups:
            return groups[0]["groupid"]

        created = self._call("hostgroup.create", {"name": _HOST_GROUP_NAME})
        return created["groupids"][0]

    def _get_icmp_template_id(self) -> str:
        templates = self._call("template.get", {"filter": {"name": [_ICMP_TEMPLATE_NAME]}})
        if not templates:
            raise ZabbixUnavailableError(
                f"Template '{_ICMP_TEMPLATE_NAME}' nao encontrado no Zabbix"
            )
        return templates[0]["templateid"]

    @staticmethod
    def _sanitize_host_name(name: str) -> str:
        return _INVALID_HOST_CHARS.sub("_", name)
