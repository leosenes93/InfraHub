import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link, useParams } from "react-router-dom";
import remarkGfm from "remark-gfm";

import { getAsset, updateAsset, type AssetPayload } from "@/api/assets";
import {
  deleteAttachment,
  listAttachments,
  uploadAttachment,
  type Attachment,
} from "@/api/attachments";
import { AssetFormModal } from "@/components/inventory/AssetFormModal";
import { AssetStatusBadge } from "@/components/inventory/AssetStatusBadge";
import { AssetTypeBadge } from "@/components/inventory/AssetTypeBadge";
import { AttachmentList } from "@/components/inventory/AttachmentList";
import { useAuth } from "@/contexts/AuthContext";
import { canDeleteAssets, canWriteAssets } from "@/lib/permissions";

export function AssetDetail() {
  const { assetId } = useParams<{ assetId: string }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const canWrite = canWriteAssets(user?.role);
  const canDelete = canDeleteAssets(user?.role);

  const [isEditingMetadata, setIsEditingMetadata] = useState(false);
  const [isEditingDocs, setIsEditingDocs] = useState(false);
  const [docsDraft, setDocsDraft] = useState("");
  const [metadataError, setMetadataError] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const {
    data: asset,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["asset", assetId],
    queryFn: () => getAsset(assetId!),
    enabled: Boolean(assetId),
  });

  const { data: attachments = [] } = useQuery({
    queryKey: ["attachments", assetId],
    queryFn: () => listAttachments(assetId!),
    enabled: Boolean(assetId),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: AssetPayload) => updateAsset(assetId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["asset", assetId] });
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      queryClient.invalidateQueries({ queryKey: ["assets-summary"] });
      setIsEditingMetadata(false);
      setIsEditingDocs(false);
    },
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadAttachment(assetId!, file),
    onSuccess: () => {
      setUploadError(null);
      queryClient.invalidateQueries({ queryKey: ["attachments", assetId] });
    },
    onError: () => {
      setUploadError("Não foi possível enviar o arquivo. Verifique o tipo e o tamanho (máx. 10MB).");
    },
  });

  const deleteAttachmentMutation = useMutation({
    mutationFn: (attachment: Attachment) => deleteAttachment(assetId!, attachment.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["attachments", assetId] }),
  });

  function startEditingDocs() {
    setDocsDraft(asset?.documentation ?? "");
    setIsEditingDocs(true);
  }

  async function saveDocumentation() {
    if (!asset) return;
    await updateMutation.mutateAsync({
      name: asset.name,
      asset_type: asset.asset_type,
      status: asset.status,
      environment: asset.environment,
      description: asset.description,
      location: asset.location,
      tags: asset.tags,
      attributes: asset.attributes,
      documentation: docsDraft,
    });
  }

  async function handleMetadataSubmit(payload: AssetPayload) {
    setMetadataError(null);
    try {
      await updateMutation.mutateAsync(payload);
    } catch {
      setMetadataError("Não foi possível salvar as alterações.");
    }
  }

  function handleDeleteAttachment(attachment: Attachment) {
    if (window.confirm(`Excluir o anexo "${attachment.filename}"?`)) {
      deleteAttachmentMutation.mutate(attachment);
    }
  }

  if (isLoading) {
    return <p className="text-sm text-slate-500">Carregando...</p>;
  }

  if (isError || !asset) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-red-600">Ativo não encontrado.</p>
        <Link to="/inventory" className="text-sm font-medium text-brand-600 hover:text-brand-700">
          Voltar ao inventário
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <Link to="/inventory" className="text-sm text-slate-500 hover:text-slate-700">
          ← Inventário
        </Link>
      </div>

      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-semibold text-slate-900">{asset.name}</h2>
            <AssetTypeBadge type={asset.asset_type} />
            <AssetStatusBadge status={asset.status} />
          </div>
          <p className="mt-1 text-sm text-slate-500">
            {asset.environment ?? "Sem ambiente"} · {asset.location ?? "Sem localização"}
          </p>
        </div>
        {canWrite && (
          <button
            onClick={() => setIsEditingMetadata(true)}
            className="rounded-md border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
          >
            Editar ativo
          </button>
        )}
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700">Documentação</h3>
          {canWrite && !isEditingDocs && (
            <button
              onClick={startEditingDocs}
              className="text-sm font-medium text-brand-600 hover:text-brand-700"
            >
              Editar
            </button>
          )}
        </div>

        {isEditingDocs ? (
          <div className="space-y-3">
            <textarea
              value={docsDraft}
              onChange={(event) => setDocsDraft(event.target.value)}
              rows={12}
              placeholder="Documentação em Markdown..."
              className="w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setIsEditingDocs(false)}
                className="rounded-md border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <button
                onClick={saveDocumentation}
                disabled={updateMutation.isPending}
                className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
              >
                {updateMutation.isPending ? "Salvando..." : "Salvar"}
              </button>
            </div>
          </div>
        ) : asset.documentation ? (
          <div className="prose prose-sm max-w-none prose-slate">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{asset.documentation}</ReactMarkdown>
          </div>
        ) : (
          <p className="text-sm text-slate-500">
            Nenhuma documentação cadastrada ainda{canWrite ? " — clique em Editar para começar." : "."}
          </p>
        )}
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h3 className="mb-4 text-sm font-semibold text-slate-700">Anexos</h3>
        <AttachmentList
          attachments={attachments}
          assetId={asset.id}
          canUpload={canWrite}
          canDelete={canDelete}
          isUploading={uploadMutation.isPending}
          uploadError={uploadError}
          onUpload={(file) => uploadMutation.mutate(file)}
          onDelete={handleDeleteAttachment}
        />
      </div>

      {isEditingMetadata && (
        <AssetFormModal
          asset={asset}
          isSubmitting={updateMutation.isPending}
          errorMessage={metadataError}
          onClose={() => {
            setIsEditingMetadata(false);
            setMetadataError(null);
          }}
          onSubmit={handleMetadataSubmit}
        />
      )}
    </div>
  );
}
