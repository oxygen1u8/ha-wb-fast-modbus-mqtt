ARG BUILD_FROM
FROM $BUILD_FROM

COPY *.toml /
COPY *.sh /
COPY *.py /
COPY fastmodbus /fastmodbus
COPY webui /webui

RUN apk add --no-cache python3 py3-pip
RUN python3 -m venv .venv
RUN .venv/bin/pip install --no-cache-dir -e .

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
