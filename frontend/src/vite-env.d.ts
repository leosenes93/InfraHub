/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_GRAFANA_URL: string;
  readonly VITE_ZABBIX_URL: string;
  readonly VITE_HEADLAMP_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
