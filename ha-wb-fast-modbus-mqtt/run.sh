#!/usr/bin/with-contenv bashio

set -e

source .venv/bin/activate

echo "Start main.py"
python3 main.py --options /data/options.json
