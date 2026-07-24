#!/usr/bin/env bash
# Sobe o ambiente de desenvolvimento do InfraHub (hot-reload em backend e frontend).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Arquivo .env nao encontrado. Copiando .env.example -> .env"
  cp .env.example .env
fi

docker compose up --build "$@"
