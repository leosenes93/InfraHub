import { apiClient } from "@/api/client";

export type AssetType = "server" | "virtual_machine" | "network_device" | "container" | "application";
export type AssetStatus = "active" | "inactive" | "maintenance" | "decommissioned";

export interface Asset {
  id: string;
  name: string;
  asset_type: AssetType;
  status: AssetStatus;
  environment: string | null;
  description: string | null;
  location: string | null;
  tags: string[];
  attributes: Record<string, unknown>;
  documentation: string | null;
  owner_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssetPayload {
  name: string;
  asset_type: AssetType;
  status: AssetStatus;
  environment?: string | null;
  description?: string | null;
  location?: string | null;
  tags?: string[];
  attributes: Record<string, unknown>;
  documentation?: string | null;
}

export interface AssetListFilters {
  asset_type?: AssetType;
  status?: AssetStatus;
  search?: string;
}

export interface AssetTypeCount {
  asset_type: AssetType;
  count: number;
}

export interface AssetStatusCount {
  status: AssetStatus;
  count: number;
}

export interface AssetSummary {
  total: number;
  by_type: AssetTypeCount[];
  by_status: AssetStatusCount[];
}

export const ASSET_TYPE_LABELS: Record<AssetType, string> = {
  server: "Servidor",
  virtual_machine: "Máquina Virtual",
  network_device: "Equipamento de Rede",
  container: "Container",
  application: "Aplicação",
};

export const ASSET_STATUS_LABELS: Record<AssetStatus, string> = {
  active: "Ativo",
  inactive: "Inativo",
  maintenance: "Manutenção",
  decommissioned: "Desativado",
};

export async function listAssets(filters: AssetListFilters = {}): Promise<Asset[]> {
  const { data } = await apiClient.get<Asset[]>("/assets", { params: filters });
  return data;
}

export async function getAsset(id: string): Promise<Asset> {
  const { data } = await apiClient.get<Asset>(`/assets/${id}`);
  return data;
}

export async function getAssetsSummary(): Promise<AssetSummary> {
  const { data } = await apiClient.get<AssetSummary>("/assets/summary");
  return data;
}

export async function createAsset(payload: AssetPayload): Promise<Asset> {
  const { data } = await apiClient.post<Asset>("/assets", payload);
  return data;
}

export async function updateAsset(id: string, payload: AssetPayload): Promise<Asset> {
  const { data } = await apiClient.patch<Asset>(`/assets/${id}`, payload);
  return data;
}

export async function deleteAsset(id: string): Promise<void> {
  await apiClient.delete(`/assets/${id}`);
}
