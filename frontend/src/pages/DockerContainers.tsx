import { useQuery } from "@tanstack/react-query";

import { listDockerContainers } from "@/api/docker";

const STATE_COLORS: Record<string, string> = {
  running: "bg-green-50 text-green-700",
  exited: "bg-slate-100 text-slate-600",
  paused: "bg-orange-50 text-orange-700",
  restarting: "bg-orange-50 text-orange-700",
  dead: "bg-red-50 text-red-700",
};

export function DockerContainers() {
  const {
    data: containers = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["docker-containers"],
    queryFn: listDockerContainers,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Docker Local</h2>
        <p className="text-sm text-slate-500">
          Containers em execução no host, lidos diretamente do socket do Docker.
        </p>
      </div>

      {isLoading && <p className="text-sm text-slate-500">Carregando...</p>}

      {isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Não foi possível conectar ao Docker
          {error instanceof Error ? `: ${error.message}` : "."}
        </div>
      )}

      {!isLoading && !isError && (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  Nome
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  Imagem
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  Estado
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  Portas
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  Criado em
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {containers.map((container) => (
                <tr key={container.id}>
                  <td className="px-4 py-3 text-sm font-medium text-slate-900">
                    {container.name}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500">{container.image}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        STATE_COLORS[container.state] ?? "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {container.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500">
                    {container.ports.length > 0 ? container.ports.join(", ") : "—"}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500">
                    {container.created_at
                      ? new Date(container.created_at).toLocaleString("pt-BR")
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
