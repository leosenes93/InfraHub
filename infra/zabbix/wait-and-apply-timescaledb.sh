#!/bin/sh
# Aguarda o zabbix-server terminar de criar o schema (tabela "history" existe)
# antes de aplicar a conversao para hypertables. Roda uma unica vez.
set -eu

export PGPASSWORD="$ZABBIX_DB_PASSWORD"
DSN="-h zabbix-postgres -U $ZABBIX_DB_USER -d $ZABBIX_DB_NAME"

echo "Aguardando o schema do Zabbix (tabela 'history')..."
until psql $DSN -tAc "SELECT to_regclass('public.history')" | grep -q history; do
  sleep 3
done

echo "Schema encontrado. Verificando se ja e uma hypertable..."
already_hypertable=$(psql $DSN -tAc "SELECT count(*) FROM timescaledb_information.hypertables WHERE hypertable_name = 'history'")

if [ "$already_hypertable" = "0" ]; then
  echo "Aplicando conversao para hypertables..."
  psql $DSN -v ON_ERROR_STOP=1 -f /timescaledb-setup.sql
  echo "Conversao concluida."
else
  echo "Ja convertido, nada a fazer."
fi
