#!/usr/bin/with-contenv bashio

set -e

source .venv/bin/activate

cat /data/options.json

echo "Start main.py"
python3 main.py --options /data/options.json
