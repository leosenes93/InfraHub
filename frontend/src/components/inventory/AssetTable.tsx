import { Link } from "react-router-dom";

import type { Asset } from "@/api/assets";
import { AssetStatusBadge } from "@/components/inventory/AssetStatusBadge";
import { AssetTypeBadge } from "@/components/inventory/AssetTypeBadge";

interface AssetTableProps {
  assets: Asset[];
  canWrite: boolean;
  canDelete: boolean;
  onEdit: (asset: Asset) => void;
  onDelete: (asset: Asset) => void;
}

export function AssetTable({ assets, canWrite, canDelete, onEdit, onDelete }: AssetTableProps) {
  if (assets.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
        Nenhum ativo encontrado.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
              Nome
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
              Tipo
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
              Status
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
              Ambiente
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
              Localização
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
              Atualizado em
            </th>
            {(canWrite || canDelete) && (
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-slate-500">
                Ações
              </th>
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {assets.map((asset) => (
            <tr key={asset.id}>
              <td className="px-4 py-3 text-sm font-medium">
                <Link to={`/inventory/${asset.id}`} className="text-brand-600 hover:text-brand-700">
                  {asset.name}
                </Link>
              </td>
              <td className="px-4 py-3">
                <AssetTypeBadge type={asset.asset_type} />
              </td>
              <td className="px-4 py-3">
                <AssetStatusBadge status={asset.status} />
              </td>
              <td className="px-4 py-3 text-sm text-slate-500">{asset.environment ?? "—"}</td>
              <td className="px-4 py-3 text-sm text-slate-500">{asset.location ?? "—"}</td>
              <td className="px-4 py-3 text-sm text-slate-500">
                {new Date(asset.updated_at).toLocaleString("pt-BR")}
              </td>
              {(canWrite || canDelete) && (
                <td className="px-4 py-3 text-right text-sm">
                  {canWrite && (
                    <button
                      onClick={() => onEdit(asset)}
                      className="mr-3 font-medium text-brand-600 hover:text-brand-700"
                    >
                      Editar
                    </button>
                  )}
                  {canDelete && (
                    <button
                      onClick={() => onDelete(asset)}
                      className="font-medium text-red-600 hover:text-red-700"
                    >
                      Excluir
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
