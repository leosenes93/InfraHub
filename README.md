# InfraHub

Plataforma web para gestão de infraestrutura de TI em ambientes corporativos — inventário, documentação técnica, monitoramento e administração de ativos centralizados em um único sistema.

> **Status:** Fase 1 — estrutura base e fundações da arquitetura. Veja o [roadmap completo](docs/roadmap.md).

## Stack

| Camada | Tecnologias |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy, Alembic, Pydantic, JWT |
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Query |
| Banco de dados | PostgreSQL |
| Cache | Redis |
| Proxy reverso | Nginx |
| Orquestração | Docker Compose |
| CI | GitHub Actions |

A stack completa (Prometheus, Grafana, Loki, Portainer, Uptime Kuma, etc.) está descrita no [roadmap](docs/roadmap.md) e será incorporada nas próximas fases.

## Arquitetura

Veja [docs/architecture.md](docs/architecture.md) para o detalhamento da arquitetura em camadas do backend, do fluxo de autenticação/RBAC e dos diagramas Mermaid.

```
InfraHub/
├── backend/    # API FastAPI (api / services / repositories / models)
├── frontend/   # SPA React + Vite + Tailwind
├── infra/      # Configuração do Nginx
├── docs/       # Documentação e diagramas
├── scripts/    # Scripts de dev/produção
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
