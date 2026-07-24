#!/usr/bin/env bash
# Sobe a stack de observabilidade e administracao acoplada ao ambiente principal.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Arquivo .env nao encontrado. Copiando .env.example -> .env"
  cp .env.example .env
fi

docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up --build -d "$@"
