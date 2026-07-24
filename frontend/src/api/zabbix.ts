import { apiClient } from "@/api/client";

export interface ZabbixProblem {
  name: string;
  severity: string;
  since: string;
}

export interface AssetMonitoringStatus {
  linked: boolean;
  zabbix_host_id: string | null;
  host_name: string | null;
  available: boolean | null;
  problems: ZabbixProblem[];
}

export async function getAssetMonitoring(assetId: string): Promise<AssetMonitoringStatus> {
  const { data } = await apiClient.get<AssetMonitoringStatus>(`/assets/${assetId}/monitoring`);
  return data;
}
