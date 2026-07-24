import { apiClient } from "@/api/client";

export interface AuditLogEntry {
  id: string;
  user_id: string | null;
  user_email: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface AuditLogFilters {
  action?: string;
  resource_type?: string;
}

export async function listAuditLogs(filters: AuditLogFilters = {}): Promise<AuditLogEntry[]> {
  const { data } = await apiClient.get<AuditLogEntry[]>("/audit-logs", { params: filters });
  return data;
}
