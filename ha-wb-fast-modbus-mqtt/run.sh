#!/usr/bin/with-contenv bashio

set -e

source .venv/bin/activate

echo "Start uvicorn"
export PATH_TO_OPTIONS="/data/options.json"
cd webui
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
