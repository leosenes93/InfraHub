import { useQuery } from "@tanstack/react-query";

import { listAuditLogs } from "@/api/audit";
import { useAuth } from "@/contexts/AuthContext";
import { isAdmin } from "@/lib/permissions";

export function AuditLog() {
  const { user } = useAuth();

  const { data: entries = [], isLoading } = useQuery({
    queryKey: ["audit-logs"],
    queryFn: () => listAuditLogs(),
    enabled: isAdmin(user?.role),
  });

  if (!isAdmin(user?.role)) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
        Apenas administradores podem visualizar o log de auditoria.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Auditoria</h2>
        <p className="text-sm text-slate-500">
          Registro de ações sensíveis: login, criação/edição/exclusão de ativos, usuários e
          anexos.
        </p>
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-500">Carregando...</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  Data/hora
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  Usuário
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  Ação
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  Recurso
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  Detalhes
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {entries.map((entry) => (
                <tr key={entry.id}>
                  <td className="px-4 py-3 text-sm text-slate-500">
                    {new Date(entry.created_at).toLocaleString("pt-BR")}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-900">
                    {entry.user_email ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono text-slate-700">{entry.action}</td>
                  <td className="px-4 py-3 text-sm text-slate-500">
                    {entry.resource_type
                      ? `${entry.resource_type}${entry.resource_id ? ` (${entry.resource_id.slice(0, 8)})` : ""}`
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">
                    {entry.details ? JSON.stringify(entry.details) : "—"}
                  </td>
                </tr>
              ))}
              {entries.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-sm text-slate-500">
                    Nenhum evento registrado ainda.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
