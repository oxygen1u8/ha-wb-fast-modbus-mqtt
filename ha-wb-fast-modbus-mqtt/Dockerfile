ARG BUILD_FROM
FROM $BUILD_FROM

COPY *.sh /
COPY *.py /
COPY requirements.txt /
COPY fastmodbus /fastmodbus

RUN apk add --no-cache python3 py3-pip
RUN python3 -m venv .venv

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
