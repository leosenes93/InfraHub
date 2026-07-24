const PLACEHOLDER_METRICS = [
  { label: "Servidores", value: "—" },
  { label: "Máquinas Virtuais", value: "—" },
  { label: "Containers", value: "—" },
  { label: "Equipamentos de Rede", value: "—" },
];

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Visão Geral</h2>
        <p className="text-sm text-slate-500">
          O inventário de ativos será conectado nesta área em uma próxima fase.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {PLACEHOLDER_METRICS.map((metric) => (
          <div
            key={metric.label}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
          >
            <p className="text-sm text-slate-500">{metric.label}</p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">{metric.value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">
        Autenticação, RBAC e infraestrutura Docker estão prontas. Os módulos de inventário, wiki
        técnica, monitoramento e auditoria chegam nas próximas fases do projeto.
      </div>
    </div>
  );
}
