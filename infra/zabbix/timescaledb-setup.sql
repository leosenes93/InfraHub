-- Converte as tabelas de historico/trends do Zabbix em hypertables do
-- TimescaleDB (compressao e retencao mais eficientes que Postgres puro).
-- So pode rodar DEPOIS que o zabbix-server ja criou o schema (primeiro start).
-- Baseado no script oficial "timescaledb.sql" do Zabbix (database/postgresql/).
SET client_min_messages = WARNING;

-- "clock" nas tabelas de historico/trends do Zabbix e INTEGER (unix
-- timestamp em segundos, 4 bytes) — confirmado no schema real (Zabbix 7.0),
-- nao BIGINT. O tipo de retorno desta funcao precisa bater exatamente com
-- o tipo da coluna de tempo do hypertable.
CREATE OR REPLACE FUNCTION zbx_ts_unix_now() RETURNS INTEGER
LANGUAGE SQL STABLE AS $$ SELECT extract(epoch FROM now())::INTEGER $$;

DROP INDEX IF EXISTS history_1;
SELECT create_hypertable('history', 'clock', chunk_time_interval => 86400, migrate_data => true, if_not_exists => true);
CREATE INDEX IF NOT EXISTS history_itemid_clock_idx ON history (itemid, clock);
SELECT set_integer_now_func('history', 'zbx_ts_unix_now', true);

DROP INDEX IF EXISTS history_uint_1;
SELECT create_hypertable('history_uint', 'clock', chunk_time_interval => 86400, migrate_data => true, if_not_exists => true);
CREATE INDEX IF NOT EXISTS history_uint_itemid_clock_idx ON history_uint (itemid, clock);
SELECT set_integer_now_func('history_uint', 'zbx_ts_unix_now', true);

DROP INDEX IF EXISTS history_str_1;
SELECT create_hypertable('history_str', 'clock', chunk_time_interval => 86400, migrate_data => true, if_not_exists => true);
CREATE INDEX IF NOT EXISTS history_str_itemid_clock_idx ON history_str (itemid, clock);
SELECT set_integer_now_func('history_str', 'zbx_ts_unix_now', true);

DROP INDEX IF EXISTS history_log_1;
SELECT create_hypertable('history_log', 'clock', chunk_time_interval => 86400, migrate_data => true, if_not_exists => true);
CREATE INDEX IF NOT EXISTS history_log_itemid_clock_idx ON history_log (itemid, clock);
SELECT set_integer_now_func('history_log', 'zbx_ts_unix_now', true);

DROP INDEX IF EXISTS history_text_1;
SELECT create_hypertable('history_text', 'clock', chunk_time_interval => 86400, migrate_data => true, if_not_exists => true);
CREATE INDEX IF NOT EXISTS history_text_itemid_clock_idx ON history_text (itemid, clock);
SELECT set_integer_now_func('history_text', 'zbx_ts_unix_now', true);

DROP INDEX IF EXISTS trends_1;
SELECT create_hypertable('trends', 'clock', chunk_time_interval => 604800, migrate_data => true, if_not_exists => true);
CREATE INDEX IF NOT EXISTS trends_itemid_clock_idx ON trends (itemid, clock);
SELECT set_integer_now_func('trends', 'zbx_ts_unix_now', true);

DROP INDEX IF EXISTS trends_uint_1;
SELECT create_hypertable('trends_uint', 'clock', chunk_time_interval => 604800, migrate_data => true, if_not_exists => true);
CREATE INDEX IF NOT EXISTS trends_uint_itemid_clock_idx ON trends_uint (itemid, clock);
SELECT set_integer_now_func('trends_uint', 'zbx_ts_unix_now', true);

UPDATE config SET db_extension = 'timescaledb', hk_history_global = 1, hk_trends_global = 1;
