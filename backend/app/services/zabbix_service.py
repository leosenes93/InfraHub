import logging
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
