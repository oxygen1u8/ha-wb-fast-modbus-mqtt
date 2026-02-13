ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip

RUN python3 -m venv .venv

COPY *.toml /
RUN .venv/bin/pip install --no-cache-dir -e .

COPY *.sh /
COPY *.py /
COPY fastmodbus /fastmodbus
COPY webui /webui

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
