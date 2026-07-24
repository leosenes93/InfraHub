-- Executado automaticamente pelo Postgres no primeiro start (mecanismo padrao
-- de /docker-entrypoint-initdb.d/), antes do zabbix-server criar seu schema.
CREATE EXTENSION IF NOT EXISTS timescaledb;
