#!/usr/bin/env bash
# Sobe a stack de monitoramento de infraestrutura externa via Zabbix,
# acoplada ao ambiente principal.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Arquivo .env nao encontrado. Copiando .env.example -> .env"
  cp .env.example .env
fi

docker compose -f docker-compose.yml -f docker-compose.zabbix.yml up --build -d "$@"
