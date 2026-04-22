FROM ghcr.io/home-assistant/base:latest

COPY pyproject.toml /ha-wb-fast-modbus-mqtt/

RUN apk add --no-cache python3 poetry

COPY *.sh /ha-wb-fast-modbus-mqtt/
COPY *.py /ha-wb-fast-modbus-mqtt/
COPY webui /ha-wb-fast-modbus-mqtt/webui

RUN chmod a+x /ha-wb-fast-modbus-mqtt/run.sh

WORKDIR /ha-wb-fast-modbus-mqtt

RUN poetry install --no-root

CMD [ "./run.sh" ]
