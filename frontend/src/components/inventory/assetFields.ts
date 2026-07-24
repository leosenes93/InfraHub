import type { AssetType } from "@/api/assets";

export interface AssetFieldDef {
  key: string;
  label: string;
  type: "text" | "number" | "select";
  options?: string[];
  required?: boolean;
}

export const ASSET_FIELDS_BY_TYPE: Record<AssetType, AssetFieldDef[]> = {
  server: [
    { key: "hostname", label: "Hostname", type: "text", required: true },
    { key: "ip_address", label: "Endereço IP", type: "text" },
    { key: "os", label: "Sistema Operacional", type: "text" },
    { key: "cpu_cores", label: "Núcleos de CPU", type: "number" },
    { key: "ram_gb", label: "RAM (GB)", type: "number" },
    { key: "disk_gb", label: "Disco (GB)", type: "number" },
  ],
  virtual_machine: [
    { key: "hostname", label: "Hostname", type: "text", required: true },
    { key: "ip_address", label: "Endereço IP", type: "text" },
    { key: "hypervisor", label: "Hypervisor", type: "text" },
    { key: "host_server", label: "Servidor físico (host)", type: "text" },
    { key: "vcpu", label: "vCPUs", type: "number" },
    { key: "ram_gb", label: "RAM (GB)", type: "number" },
    { key: "disk_gb", label: "Disco (GB)", type: "number" },
  ],
  network_device: [
    {
      key: "device_type",
      label: "Tipo de equipamento",
      type: "select",
      options: ["switch", "router", "firewall", "access_point", "load_balancer"],
      required: true,
    },
    { key: "ip_address", label: "Endereço IP", type: "text" },
    { key: "vendor", label: "Fabricante", type: "text" },
    { key: "model", label: "Modelo", type: "text" },
    { key: "firmware_version", label: "Versão do firmware", type: "text" },
  ],
  container: [
    { key: "image", label: "Imagem", type: "text", required: true },
    { key: "host_server", label: "Host", type: "text" },
    { key: "orchestrator", label: "Orquestrador", type: "text" },
  ],
  application: [
    { key: "repository_url", label: "URL do repositório", type: "text" },
    { key: "version", label: "Versão", type: "text" },
    { key: "language", label: "Linguagem", type: "text" },
    { key: "deployment_url", label: "URL de deploy", type: "text" },
  ],
};
