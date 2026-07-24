import { apiClient } from "@/api/client";
import type { Asset } from "@/api/assets";

export interface SearchResponse {
  query: string;
  results: Asset[];
}

export async function searchGlobal(query: string): Promise<SearchResponse> {
  const { data } = await apiClient.get<SearchResponse>("/search", { params: { q: query } });
  return data;
}
