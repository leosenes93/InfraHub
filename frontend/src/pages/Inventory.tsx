import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import {
  ASSET_TYPE_LABELS,
  createAsset,
  deleteAsset,
  listAssets,
  updateAsset,
  type Asset,
  type AssetPayload,
  type AssetType,
} from "@/api/assets";
import { AssetFormModal } from "@/components/inventory/AssetFormModal";
import { AssetTable } from "@/components/inventory/AssetTable";
import { useAuth } from "@/contexts/AuthContext";
import { canDeleteAssets, canWriteAssets } from "@/lib/permissions";

const TYPE_FILTERS: { label: string; value: AssetType | "all" }[] = [
  { label: "Todos", value: "all" },
  ...(Object.entries(ASSET_TYPE_LABELS) as [AssetType, string][]).map(([value, label]) => ({
    label,
    value,
  })),
];

export function Inventory() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [typeFilter, setTypeFilter] = useState<AssetType | "all">("all");
  const [search, setSearch] = useState("");
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const canWrite = canWriteAssets(user?.role);
  const canDelete = canDeleteAssets(user?.role);

  const { data: assets = [], isLoading } = useQuery({
    queryKey: ["assets", typeFilter, search],
    queryFn: () =>
      listAssets({
        asset_type: typeFilter === "all" ? undefined : typeFilter,
        search: search || undefined,
      }),
  });

  const invalidateAssets = () => {
    queryClient.invalidateQueries({ queryKey: ["assets"] });
    queryClient.invalidateQueries({ queryKey: ["assets-summary"] });
  };

  const createMutation = useMutation({
    mutationFn: createAsset,
    onSuccess: () => {
      invalidateAssets();
      setIsCreating(false);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: AssetPayload }) => updateAsset(id, payload),
    onSuccess: () => {
      invalidateAssets();
      setEditingAsset(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAsset,
    onSuccess: invalidateAssets,
  });

  async function handleFormSubmit(payload: AssetPayload) {
    setFormError(null);
    try {
      if (editingAsset) {
        await updateMutation.mutateAsync({ id: editingAsset.id, payload });
      } else {
        await createMutation.mutateAsync(payload);
      }
    } catch {
      setFormError("Não foi possível salvar o ativo. Verifique os campos e tente novamente.");
    }
  }

  function handleDelete(asset: Asset) {
    if (window.confirm(`Excluir o ativo "${asset.name}"? Esta ação não pode ser desfeita.`)) {
      deleteMutation.mutate(asset.id);
    }
  }

  const isFormOpen = isCreating || editingAsset !== null;
  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Inventário de Ativos</h2>
          <p className="text-sm text-slate-500">
            Servidores, máquinas virtuais, equipamentos de rede, containers e aplicações.
          </p>
        </div>
        {canWrite && (
          <button
            onClick={() => setIsCreating(true)}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            Novo Ativo
          </button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {TYPE_FILTERS.map((filter) => (
          <button
            key={filter.value}
            onClick={() => setTypeFilter(filter.value)}
            className={`rounded-full px-3 py-1.5 text-sm font-medium ${
              typeFilter === filter.value
                ? "bg-brand-600 text-white"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            {filter.label}
          </button>
        ))}
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Buscar por nome..."
          className="ml-auto w-64 rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        />
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-500">Carregando...</p>
      ) : (
        <AssetTable
          assets={assets}
          canWrite={canWrite}
          canDelete={canDelete}
          onEdit={setEditingAsset}
          onDelete={handleDelete}
        />
      )}

      {isFormOpen && (
        <AssetFormModal
          asset={editingAsset}
          isSubmitting={isSubmitting}
          errorMessage={formError}
          onClose={() => {
            setIsCreating(false);
            setEditingAsset(null);
            setFormError(null);
          }}
          onSubmit={handleFormSubmit}
        />
      )}
    </div>
  );
}
