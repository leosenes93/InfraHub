# InfraHub

Plataforma web para gestão de infraestrutura de TI em ambientes corporativos — inventário, documentação técnica, monitoramento e administração de ativos centralizados em um único sistema.

> **Status:** Fase 2 — observabilidade e administração. Veja o [roadmap completo](docs/roadmap.md).

## Stack

| Camada | Tecnologias |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy, Alembic, Pydantic, JWT |
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Query |
| Banco de dados | PostgreSQL |
| Cache | Redis |
| Proxy reverso | Nginx |
| Observabilidade | Prometheus, Grafana, Loki, Promtail, cAdvisor, Node Exporter |
| Administração | Portainer, Uptime Kuma |
| Orquestração | Docker Compose |
| CI | GitHub Actions |

## Arquitetura

Veja [docs/architecture.md](docs/architecture.md) para o detalhamento da arquitetura em camadas do backend, do fluxo de autenticação/RBAC e dos diagramas Mermaid.

```
InfraHub/
├── backend/    # API FastAPI (api / services / repositories / models)
├── frontend/   # SPA React + Vite + Tailwind
├── infra/      # Nginx, Prometheus, Loki, Promtail, Grafana (provisioning + dashboards)
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

## Papéis de acesso (RBAC)

| Perfil | Descrição |
| --- | --- |
| Administrador | Acesso total, incluindo gestão de usuários |
| Analista | Acesso de análise/edição avançada (módulos futuros) |
| Operador | Operações do dia a dia sobre os ativos (módulos futuros) |
| Visualizador | Somente leitura |

## Variáveis de ambiente

Todas as variáveis estão documentadas em [.env.example](.env.example). Nunca commite um `.env` real — o `.gitignore` já bloqueia isso.

## Contribuindo

O projeto é desenvolvido de forma incremental, fase a fase — veja o [roadmap](docs/roadmap.md) para o que já foi entregue e o que vem a seguir.
