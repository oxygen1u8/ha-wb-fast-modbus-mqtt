ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip

RUN python3 -m venv .venv

COPY requirements.txt /
RUN .venv/bin/pip install --no-cache-dir -r /requirements.txt

COPY *.sh /
COPY *.py /
COPY fastmodbus /fastmodbus
COPY webapp /webapp

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
