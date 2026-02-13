#!/usr/bin/with-contenv bashio

set -e

source .venv/bin/activate

echo "Start main.py"
ha-wb-fast-modbus-mqtt --options /data/options.json
