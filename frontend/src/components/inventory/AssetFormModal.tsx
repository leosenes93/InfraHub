import { useState, type FormEvent } from "react";

import {
  ASSET_STATUS_LABELS,
  ASSET_TYPE_LABELS,
  type Asset,
  type AssetPayload,
  type AssetStatus,
  type AssetType,
} from "@/api/assets";
import { ASSET_FIELDS_BY_TYPE } from "@/components/inventory/assetFields";

const ASSET_TYPES = Object.keys(ASSET_TYPE_LABELS) as AssetType[];
const ASSET_STATUSES = Object.keys(ASSET_STATUS_LABELS) as AssetStatus[];

const inputClass =
  "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500";
const labelClass = "mb-1 block text-sm font-medium text-slate-700";

interface AssetFormModalProps {
  asset: Asset | null;
  onClose: () => void;
  onSubmit: (payload: AssetPayload) => Promise<void>;
  isSubmitting: boolean;
  errorMessage: string | null;
}

function attributesToStrings(attributes: Record<string, unknown>): Record<string, string> {
  const result: Record<string, string> = {};
  for (const [key, value] of Object.entries(attributes)) {
    if (value !== null && value !== undefined) {
      result[key] = String(value);
    }
  }
  return result;
}

export function AssetFormModal({ asset, onClose, onSubmit, isSubmitting, errorMessage }: AssetFormModalProps) {
  const [name, setName] = useState(asset?.name ?? "");
  const [assetType, setAssetType] = useState<AssetType>(asset?.asset_type ?? "server");
  const [status, setStatus] = useState<AssetStatus>(asset?.status ?? "active");
  const [environment, setEnvironment] = useState(asset?.environment ?? "");
  const [location, setLocation] = useState(asset?.location ?? "");
  const [description, setDescription] = useState(asset?.description ?? "");
  const [tags, setTags] = useState(asset?.tags.join(", ") ?? "");
  const [attributeValues, setAttributeValues] = useState<Record<string, string>>(
    attributesToStrings(asset?.attributes ?? {})
  );

  function handleTypeChange(newType: AssetType) {
    setAssetType(newType);
    setAttributeValues({});
  }

  function handleAttributeChange(key: string, value: string) {
    setAttributeValues((previous) => ({ ...previous, [key]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const fields = ASSET_FIELDS_BY_TYPE[assetType];
    const attributes: Record<string, unknown> = {};
    for (const field of fields) {
      const raw = attributeValues[field.key];
      if (raw === undefined || raw === "") continue;
      attributes[field.key] = field.type === "number" ? Number(raw) : raw;
    }

    await onSubmit({
      name,
      asset_type: assetType,
      status,
      environment: environment || null,
      location: location || null,
      description: description || null,
      tags: tags
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
      attributes,
    });
  }

  const fields = ASSET_FIELDS_BY_TYPE[assetType];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
      <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white p-6 shadow-lg">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">
          {asset ? "Editar ativo" : "Novo ativo"}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Nome</label>
              <input
                required
                value={name}
                onChange={(event) => setName(event.target.value)}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Tipo</label>
              <select
                value={assetType}
                onChange={(event) => handleTypeChange(event.target.value as AssetType)}
                className={inputClass}
              >
                {ASSET_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {ASSET_TYPE_LABELS[type]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Status</label>
              <select
                value={status}
                onChange={(event) => setStatus(event.target.value as AssetStatus)}
                className={inputClass}
              >
                {ASSET_STATUSES.map((value) => (
                  <option key={value} value={value}>
                    {ASSET_STATUS_LABELS[value]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Ambiente</label>
              <input
                value={environment}
                onChange={(event) => setEnvironment(event.target.value)}
                placeholder="production, staging..."
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Localização</label>
              <input
                value={location}
                onChange={(event) => setLocation(event.target.value)}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Tags (separadas por vírgula)</label>
              <input
                value={tags}
                onChange={(event) => setTags(event.target.value)}
                className={inputClass}
              />
            </div>
          </div>

          <div>
            <label className={labelClass}>Descrição</label>
            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={2}
              className={inputClass}
            />
          </div>

          <div className="border-t border-slate-200 pt-4">
            <h3 className="mb-3 text-sm font-semibold text-slate-700">
              Detalhes de {ASSET_TYPE_LABELS[assetType]}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {fields.map((field) => (
                <div key={field.key}>
                  <label className={labelClass}>{field.label}</label>
                  {field.type === "select" ? (
                    <select
                      required={field.required}
                      value={attributeValues[field.key] ?? ""}
                      onChange={(event) => handleAttributeChange(field.key, event.target.value)}
                      className={inputClass}
                    >
                      <option value="" disabled>
                        Selecione
                      </option>
                      {field.options?.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      required={field.required}
                      type={field.type === "number" ? "number" : "text"}
                      value={attributeValues[field.key] ?? ""}
                      onChange={(event) => handleAttributeChange(field.key, event.target.value)}
                      className={inputClass}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {errorMessage && <p className="text-sm text-red-600">{errorMessage}</p>}

          <div className="flex justify-end gap-3 border-t border-slate-200 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
            >
              {isSubmitting ? "Salvando..." : "Salvar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
