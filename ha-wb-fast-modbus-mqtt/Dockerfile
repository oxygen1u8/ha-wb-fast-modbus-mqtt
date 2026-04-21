FROM ghcr.io/home-assistant/base:latest

COPY requirements.txt /tmp/requirements.txt

RUN apk add --no-cache python3 py3-pip && \
    python3 -m venv /ha-wb-fast-modbus-mqtt/.venv && \
    /ha-wb-fast-modbus-mqtt/.venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /tmp/requirements.txt

COPY *.sh /ha-wb-fast-modbus-mqtt/
COPY *.py /ha-wb-fast-modbus-mqtt/
COPY webui /ha-wb-fast-modbus-mqtt/webui

RUN chmod a+x /ha-wb-fast-modbus-mqtt/run.sh

WORKDIR /ha-wb-fast-modbus-mqtt

CMD [ "./run.sh" ]
