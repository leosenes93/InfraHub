import { ASSET_STATUS_LABELS, type AssetStatus } from "@/api/assets";

const COLORS: Record<AssetStatus, string> = {
  active: "bg-green-50 text-green-700",
  inactive: "bg-slate-100 text-slate-600",
  maintenance: "bg-orange-50 text-orange-700",
  decommissioned: "bg-red-50 text-red-700",
};

export function AssetStatusBadge({ status }: { status: AssetStatus }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${COLORS[status]}`}>
      {ASSET_STATUS_LABELS[status]}
    </span>
  );
}
