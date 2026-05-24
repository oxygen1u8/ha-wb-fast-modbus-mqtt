FROM ghcr.io/home-assistant/base:latest

COPY pyproject.toml /ha-wb-fast-modbus-mqtt/

RUN apk add --no-cache python3 poetry git jinja2-cli make

COPY *.sh /ha-wb-fast-modbus-mqtt/
COPY *.py /ha-wb-fast-modbus-mqtt/
COPY webui /ha-wb-fast-modbus-mqtt/webui

RUN chmod a+x /ha-wb-fast-modbus-mqtt/run.sh

WORKDIR /ha-wb-fast-modbus-mqtt

RUN poetry install --no-root

RUN git clone https://github.com/wirenboard/wb-mqtt-serial.git /wb-mqtt-serial && \
    cd /wb-mqtt-serial && \
    git checkout f947494 && \
    ln -s /usr/bin/jinja2 /usr/bin/j2 && \
    make templates && \
    cp -r /wb-mqtt-serial/build/templates /ha-wb-fast-modbus-mqtt

CMD [ "./run.sh" ]
