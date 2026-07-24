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

## Fase 3 — Inventário de ativos ✅

- Modelo único `assets` (Servidores, Máquinas Virtuais, Equipamentos de Rede, Containers e Aplicações) com atributos específicos por tipo em JSONB, validados via Pydantic.
- CRUD completo com RBAC por operação: Visualizador só lê; Operador e Analista leem/criam/editam; Administrador tudo, incluindo excluir.
- Página de Inventário no frontend com filtro por tipo, busca e formulário adaptável por tipo de ativo.
- Dashboard real (contagens por tipo/status via `GET /assets/summary`), substituindo os indicadores mockados da Fase 1.

## Fase 4 — Wiki técnica e documentação de ativos ✅

- Documentação em Markdown por ativo (`assets.documentation`), editada e renderizada (com preview) na página de detalhe de cada ativo.
- Upload de diagramas e documentos por ativo (`asset_attachments`), armazenados em `storage/uploads/<asset_id>/`, com listagem, download e exclusão.
- RBAC: upload segue a mesma regra de escrita do inventário (Admin/Analista/Operador); exclusão de anexos restrita a Administrador.
- Validação de tipo de arquivo (imagens, PDF, texto/Markdown) e tamanho máximo (10MB, configurável).

## Fase 5 — Integrações e automações ✅

- **Docker**: `GET /docker/containers` lista os containers do host em tempo real via socket do Docker (montado somente leitura); página "Docker Local" no frontend.
- **Auditoria**: tabela `audit_logs` registrando login (sucesso/falha), criação de usuário, criar/editar/excluir ativo e upload/exclusão de anexo — quem fez, quando, de qual IP. `GET /audit-logs` e página "Auditoria" restritos a Administrador.
- **Busca global**: `GET /search` combina `ILIKE` com `similarity()` (extensão `pg_trgm` do Postgres) sobre nome/descrição dos ativos; campo de busca no cabeçalho, disponível em qualquer página.
- Integração com Zabbix/Prometheus para status/alertas de ativos externos permanece como item futuro (fora do escopo desta fase).

## Fase 6 — Preparação para Kubernetes ✅

- Chart Helm em `k8s/infrahub/` para o núcleo da aplicação (backend, web/Nginx, Postgres, Redis) — ver [docs/kubernetes.md](kubernetes.md) para o mapeamento completo Compose → Kubernetes.
- Configuração externalizada via `ConfigMap`/`Secret`; probes de liveness/readiness reaproveitando `/api/v1/health` e `/api/v1/health/ready`.
- Validado com uma instalação real em um cluster `kind` descartável (não só `helm lint`/`template`) — encontrou e corrigiu dois bugs reais, incluindo uma condição de corrida no seed do admin inicial que já existia desde a Fase 1 no `docker-compose.prod.yml`.
- Observabilidade (Prometheus/Grafana/Loki/Portainer/Uptime Kuma) e integração Zabbix/Prometheus permanecem fora do escopo — produção real usaria charts prontos (ex.: `kube-prometheus-stack`) para a primeira.

---

Cada fase é discutida e aprovada antes da implementação, conforme o modelo incremental adotado no projeto.
