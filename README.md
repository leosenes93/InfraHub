# InfraHub

Plataforma web para gestão de infraestrutura de TI em ambientes corporativos — inventário, documentação técnica, monitoramento e administração de ativos centralizados em um único sistema.

> **Status:** Fase 9 — k3s. Veja o [roadmap completo](docs/roadmap.md).

## Stack

| Camada | Tecnologias |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy, Alembic, Pydantic, JWT |
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Query |
| Banco de dados | PostgreSQL |
| Cache | Redis |
| Proxy reverso | Nginx |
| Observabilidade | Prometheus, Grafana, Loki, Promtail, cAdvisor, Node Exporter |
| Monitoramento de infraestrutura | Zabbix (Postgres + TimescaleDB dedicado) |
| Administração | Portainer, Uptime Kuma |
| Orquestração | Docker Compose, Kubernetes, OpenShift Local, k3s |
| CI | GitHub Actions |

## Arquitetura

Veja [docs/architecture.md](docs/architecture.md) para o detalhamento da arquitetura em camadas do backend, do fluxo de autenticação/RBAC e dos diagramas Mermaid.

```
InfraHub/
├── backend/    # API FastAPI (api / services / repositories / models)
├── frontend/   # SPA React + Vite + Tailwind
├── infra/      # Nginx, Prometheus, Loki, Promtail, Grafana (provisioning + dashboards)
├── k8s/        # Chart Helm (núcleo da aplicação em Kubernetes)
├── docs/       # Documentação e diagramas
├── scripts/    # Scripts de dev/produção/observabilidade
└── .github/    # Workflows de CI
```

## Como rodar

Pré-requisitos: [Docker](https://www.docker.com/) e Docker Compose.

```bash
cp .env.example .env   # ajuste os segredos antes de produção
./scripts/dev.sh        # Linux/macOS
# ou
./scripts/dev.ps1       # Windows (PowerShell)
```

Isso sobe Postgres, Redis, backend (com hot-reload), frontend (com hot-reload) e Nginx. A aplicação fica disponível em `http://localhost:8080`.

Um usuário administrador é criado automaticamente no primeiro start, usando as credenciais definidas em `INITIAL_ADMIN_EMAIL` / `INITIAL_ADMIN_PASSWORD` no `.env` (padrão: `admin@infrahub.io` / `change-me` — **troque antes de expor o ambiente**).

A documentação interativa da API (Swagger UI) fica em `http://localhost:8080/api/v1/docs`.

### Produção

```bash
cp .env.example .env   # defina segredos fortes
./scripts/prod.sh       # Linux/macOS
# ou
./scripts/prod.ps1      # Windows (PowerShell)
```

Usa `docker-compose.prod.yml`: backend com múltiplos workers Uvicorn e sem bind mounts; Nginx serve o build estático do frontend diretamente (sem o container `frontend` de desenvolvimento).

### Rodando os testes do backend

```bash
docker compose exec backend uv run pytest
```

## Observabilidade e administração

Stack adicional e **acoplável** ao ambiente principal (não substitui `scripts/dev.sh`, soma-se a ele):

```bash
./scripts/monitoring.sh   # Linux/macOS
# ou
./scripts/monitoring.ps1  # Windows (PowerShell)
```

Isso sobe, combinado ao `docker-compose.yml`: Prometheus, Grafana, Loki, Promtail, cAdvisor, Node Exporter, exporters de Postgres/Redis, Portainer e Uptime Kuma.

| Ferramenta | URL padrão | Observação |
| --- | --- | --- |
| Grafana | http://localhost:3000 | Login via `GRAFANA_ADMIN_USER`/`GRAFANA_ADMIN_PASSWORD` do `.env`. Datasources (Prometheus, Loki) e o dashboard "InfraHub - Visão Geral" já vêm provisionados. |
| Prometheus | http://localhost:9090 | Métricas do backend (`/metrics`), Postgres, Redis, containers e host. |
| Portainer | http://localhost:9000 | **Primeiro acesso**: defina a senha de admin pela UI dentro da janela inicial (alguns minutos após o start) — não há provisionamento automático de senha. |
| Uptime Kuma | http://localhost:3001 | **Primeiro acesso**: crie a conta de admin pela UI. Configure monitores apontando para `http://nginx/healthz`, `http://backend:8000/api/v1/health`, etc. |
| cAdvisor | http://localhost:8081 | Métricas de containers (consumidas pelo Prometheus). |
| Node Exporter | http://localhost:9100 | Métricas do host (consumidas pelo Prometheus). |

**Notas de segurança (ambiente local/dev):** cAdvisor e Promtail montam o socket do Docker em modo somente leitura; Portainer monta em leitura/escrita, pois precisa gerenciar containers. Isso é inerente a essas ferramentas — em um deploy real, mantenha essas portas fora de qualquer exposição pública e restrinja o acesso ao socket do Docker.

**Nota sobre métricas por container:** em Docker Desktop (Windows/Mac) com o *containerd image store* (padrão atual), o cAdvisor não consegue enumerar containers individualmente — só expõe métricas agregadas de todos os containers. Em um host Linux real com o driver `overlay2`, o detalhamento por container funciona plenamente; é assim que o dashboard deve ser lido em produção.

O endpoint `/metrics` do backend não é exposto pelo Nginx (que só faz proxy de `/api/` e `/`) — só é alcançável dentro da rede Docker interna, por isso não requer autenticação própria.

## Inventário de ativos

Acesse `http://localhost:8080/inventory` (autenticado) para gerenciar Servidores, Máquinas Virtuais, Equipamentos de Rede, Containers e Aplicações — uma página unificada com filtro por tipo, busca e formulário que adapta os campos ao tipo de ativo selecionado. O dashboard (`/`) mostra contagens reais por tipo e status.

API: `GET/POST /api/v1/assets`, `GET/PATCH/DELETE /api/v1/assets/{id}`, `GET /api/v1/assets/summary` — ver RBAC abaixo para quem pode criar/editar/excluir.

## Wiki técnica e anexos

Cada ativo tem uma página de detalhe (`/inventory/{id}`, clique no nome na tabela) com:

- **Documentação em Markdown** — editor com preview renderizado (`react-markdown`), salva via `PATCH /api/v1/assets/{id}`.
- **Anexos** — upload de diagramas/documentos (imagens PNG/JPEG/SVG, PDF, texto/Markdown, até 10MB), listados com download e exclusão via `/api/v1/assets/{id}/attachments`.

Os arquivos ficam em `storage/uploads/<asset_id>/` (volume Docker, fora do controle de versão — já reservado no `.gitignore`). Ao excluir um ativo, seus anexos em disco também são removidos.

## Integrações e automações

- **Docker Local** (`/docker`) — lista os containers em execução no host em tempo real, lidos via socket do Docker (montado somente leitura no backend). `GET /api/v1/docker/containers`.
- **Auditoria** (`/audit`, só Administrador) — registro de login (sucesso/falha), criação de usuário e criar/editar/excluir ativos e anexos, com usuário, ação, recurso e IP. `GET /api/v1/audit-logs`.
- **Busca global** — campo no cabeçalho (qualquer página), busca ativos por nome/descrição usando `pg_trgm` do Postgres (tolerante a pequenas variações/erros de digitação). `GET /api/v1/search?q=`.

**Nota de segurança:** o socket do Docker é montado somente leitura no backend (mesma lógica já aplicada ao cAdvisor/Promtail na Fase 2) — suficiente para listar containers, mas ainda expõe informações do host; mantenha essa montagem restrita a ambientes de confiança.

## Monitoramento com Zabbix

Stack adicional e **acoplável** ao ambiente principal (mesmo padrão da observabilidade acima):

```bash
./scripts/zabbix.sh   # Linux/macOS
# ou
./scripts/zabbix.ps1  # Windows (PowerShell)
```

Isso sobe um Zabbix completo (servidor, interface web, agente de exemplo e Postgres dedicado com TimescaleDB). Interface web em `http://localhost:8082` (login inicial `Admin` / `zabbix` — troque antes de expor o ambiente; também tem atalho no menu "Zabbix" do InfraHub). Depois de gerar um token de API e configurá-lo em `ZABBIX_API_TOKEN` no `.env`, qualquer ativo do inventário pode ser vinculado a um host do Zabbix — manualmente (campo "ID do host no Zabbix" no formulário de edição) ou automaticamente (botão "Criar host no Zabbix", disponível para ativos com IP cadastrado). A página do ativo passa a mostrar disponibilidade e problemas ativos ao vivo, via `GET /api/v1/assets/{id}/monitoring`.

Veja [docs/zabbix.md](docs/zabbix.md) para a arquitetura completa, o passo a passo de geração do token de API e por que a porta `10051` fica exposta (preparação para agentes em VMs no Hyper-V).

## Kubernetes

O núcleo da aplicação também roda em Kubernetes via o chart Helm em [`k8s/infrahub/`](k8s/infrahub/):

```bash
helm install infrahub k8s/infrahub \
  --set postgres.password=<senha-forte> \
  --set secrets.jwtSecretKey=<chave-longa-aleatoria> \
  --set secrets.initialAdminPassword=<senha-forte>
```

Veja [docs/kubernetes.md](docs/kubernetes.md) para o mapeamento completo Compose → Kubernetes, pré-requisitos e limitações conhecidas.

## OpenShift Local

O mesmo chart Helm também roda em [OpenShift Local](https://developers.redhat.com/products/openshift-local) (CRC), com builds das imagens acontecendo dentro do próprio cluster (sem depender de Docker Desktop):

```bash
oc new-project infrahub
oc adm policy add-scc-to-user anyuid -z default -n infrahub
oc new-build --name=infrahub-backend --binary --strategy=docker -n infrahub
oc new-build --name=infrahub-web --binary --strategy=docker -n infrahub
oc patch bc/infrahub-web -n infrahub --type=json \
  -p '[{"op":"add","path":"/spec/strategy/dockerStrategy/dockerfilePath","value":"infra/nginx/Dockerfile.prod"}]'
```

Veja [docs/openshift.md](docs/openshift.md) para o passo a passo completo — inclui dois bugs reais do CRC no Windows (e como contorná-los) e dois bugs reais de build corrigidos no repositório (`.dockerignore`, `Dockerfile.prod`) que beneficiam qualquer pipeline de build rootless.

## k3s

Alternativa mais leve ao OpenShift Local — mesmo chart Helm, mesma capacidade de orquestração real, mas cabendo confortavelmente numa VM de 2GB RAM / 20GB disco (o CRC pede 12GB RAM / 60GB disco fixo):

```bash
curl -sfL https://get.k3s.io | sh -
helm install infrahub k8s/infrahub -f k8s/infrahub/values-k3s.yaml
```

Veja [docs/k3s.md](docs/k3s.md) para o passo a passo completo — inclui bugs reais encontrados (Secure Boot com template errado para VMs Linux no Hyper-V, partição LVM subalocada travando o disco, senhas com caracteres especiais quebrando a URL de conexão do Postgres, variáveis `VITE_*` que precisam ser passadas em tempo de build, não runtime).

O mesmo cluster também roda **Grafana + Prometheus**, **Zabbix** (com os agentes das VMs de domínio reportando pra ele) e o **Headlamp** (painel web do cluster, sucessor mantido do Kubernetes Dashboard, que foi arquivado) — manifests em `k8s/monitoring/` e `k8s/zabbix/`.

## Papéis de acesso (RBAC)

| Perfil | Descrição |
| --- | --- |
| Administrador | Acesso total, incluindo gestão de usuários e exclusão de ativos |
| Analista | Lê e cria/edita ativos do inventário |
| Operador | Lê e cria/edita ativos do inventário |
| Visualizador | Somente leitura |

## Variáveis de ambiente

Todas as variáveis estão documentadas em [.env.example](.env.example). Nunca commite um `.env` real — o `.gitignore` já bloqueia isso.

## Contribuindo

O projeto é desenvolvido de forma incremental, fase a fase — veja o [roadmap](docs/roadmap.md) para o que já foi entregue e o que vem a seguir.
