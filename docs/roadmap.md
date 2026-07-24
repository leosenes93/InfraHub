# Roadmap — InfraHub

O projeto é construído de forma incremental. A Fase 1 entrega o núcleo (autenticação, arquitetura, infraestrutura Docker); as fases seguintes adicionam observabilidade, administração e as funcionalidades de negócio.

## Fase 1 — Estrutura base e fundações ✅

- Arquitetura em camadas no backend (api / services / repositories / models).
- Autenticação JWT com RBAC (Administrador, Analista, Operador, Visualizador).
- Banco versionado com Alembic, logging estruturado, health checks.
- Frontend React + Vite + Tailwind + React Query, com login e layout base.
- Docker Compose para dev e produção, Nginx como proxy reverso.
- CI (GitHub Actions) com lint, testes e build.

## Fase 2 — Observabilidade e administração ✅

- **Prometheus**: coleta métricas do backend (`prometheus-fastapi-instrumentator`), Postgres, Redis, containers (cAdvisor) e host (Node Exporter).
- **Grafana**: datasources (Prometheus, Loki) e dashboard "InfraHub - Visão Geral" provisionados como código.
- **Loki + Promtail**: agregação centralizada dos logs estruturados, coletados via descoberta automática de containers no Docker.
- **cAdvisor** e **Node Exporter**: métricas de containers e do host.
- **Portainer**: administração visual dos containers Docker (setup de admin manual no primeiro acesso).
- **Uptime Kuma**: monitoramento de disponibilidade dos serviços (monitores configurados manualmente).
- `docker-compose.monitoring.yml`, acoplável ao ambiente principal via `scripts/monitoring.sh` / `.ps1`.

## Fase 3 — Inventário de ativos

- Modelagem de Servidores, Máquinas Virtuais, Equipamentos de Rede, Containers e Aplicações.
- CRUD completo com RBAC por operação (ex.: Visualizador só lê, Operador edita, Administrador tudo).
- Dashboard real substituindo os indicadores mockados da Fase 1.

## Fase 4 — Wiki técnica e documentação de ativos

- Editor de conteúdo por ativo (Markdown).
- Upload de diagramas e documentos (armazenamento em volume dedicado, `storage/uploads/`).

## Fase 5 — Integrações e automações

- Integração com Docker (listar containers locais do host via socket).
- Integração futura com Zabbix e Prometheus para status/alertas de ativos externos.
- Registro de auditoria (quem fez o quê, quando) para todas as ações sensíveis.
- Busca global (provavelmente via índice em Postgres — `pg_trgm`/full text search — antes de considerar Elasticsearch).

## Fase 6 — Preparação para Kubernetes

- Helm charts ou manifests Kustomize equivalentes aos serviços do Compose.
- Externalização de configuração via ConfigMap/Secret.
- Probes de liveness/readiness reaproveitando os endpoints `/health` e `/health/ready`.

---

Cada fase é discutida e aprovada antes da implementação, conforme o modelo incremental adotado no projeto.
