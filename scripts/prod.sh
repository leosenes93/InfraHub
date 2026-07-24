#!/usr/bin/env bash
# Sobe o ambiente de producao do InfraHub (imagens otimizadas, sem hot-reload).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Arquivo .env nao encontrado. Copie .env.example para .env e ajuste os segredos antes de continuar." >&2
  exit 1
fi

docker compose -f docker-compose.prod.yml up --build -d "$@"
