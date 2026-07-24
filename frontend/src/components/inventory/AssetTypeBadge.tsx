import { ASSET_TYPE_LABELS, type AssetType } from "@/api/assets";

const COLORS: Record<AssetType, string> = {
  server: "bg-blue-50 text-blue-700",
  virtual_machine: "bg-purple-50 text-purple-700",
  network_device: "bg-amber-50 text-amber-700",
  container: "bg-cyan-50 text-cyan-700",
  application: "bg-emerald-50 text-emerald-700",
};

export function AssetTypeBadge({ type }: { type: AssetType }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${COLORS[type]}`}>
      {ASSET_TYPE_LABELS[type]}
    </span>
  );
}
