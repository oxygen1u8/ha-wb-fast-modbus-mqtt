#!/usr/bin/with-contenv bashio

set -e

export PATH_TO_OPTIONS="/data/options.json"
export PATH_TO_TEMPLATES="/ha-wb-fast-modbus-mqtt/templates"
export DB_PATH="/data/modbus.db"
export DATABASE_URL="sqlite+aiosqlite:///$DB_PATH"

cd webui

if [ -f "${DB_PATH}" ]; then
    bashio::log.info "Database found, applying Alembic migrations"
else
    bashio::log.info "Database not found, initializing schema with Alembic"
fi
poetry run alembic upgrade head

poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
