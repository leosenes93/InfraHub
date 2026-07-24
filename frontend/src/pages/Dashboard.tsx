import { useQuery } from "@tanstack/react-query";

import { ASSET_TYPE_LABELS, getAssetsSummary, type AssetType } from "@/api/assets";

const METRIC_TYPES: AssetType[] = ["server", "virtual_machine", "network_device", "container"];

export function Dashboard() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ["assets-summary"],
    queryFn: getAssetsSummary,
  });

  const countByType = new Map(summary?.by_type.map((item) => [item.asset_type, item.count]));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Visão Geral</h2>
        <p className="text-sm text-slate-500">
          Indicadores do inventário de infraestrutura, atualizados em tempo real.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {METRIC_TYPES.map((type) => (
          <div key={type} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">{ASSET_TYPE_LABELS[type]}</p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {isLoading ? "—" : (countByType.get(type) ?? 0)}
            </p>
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h3 className="mb-4 text-sm font-semibold text-slate-700">Total de ativos por status</h3>
        {isLoading || !summary ? (
          <p className="text-sm text-slate-500">Carregando...</p>
        ) : summary.total === 0 ? (
          <p className="text-sm text-slate-500">
            Nenhum ativo cadastrado ainda. Acesse o Inventário para adicionar o primeiro.
          </p>
        ) : (
          <ul className="space-y-2">
            {summary.by_status.map((item) => (
              <li key={item.status} className="flex items-center justify-between text-sm">
                <span className="capitalize text-slate-600">{item.status}</span>
                <span className="font-medium text-slate-900">{item.count}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">
        Autenticação, RBAC, infraestrutura Docker, observabilidade e o inventário de ativos estão
        prontos. Wiki técnica e auditoria chegam nas próximas fases do projeto.
      </div>
    </div>
  );
}
