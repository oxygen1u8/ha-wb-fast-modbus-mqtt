ARG BUILD_FROM
FROM $BUILD_FROM

COPY *.toml /
COPY requirements.txt /
COPY *.sh /
COPY *.py /
COPY fastmodbus /fastmodbus
COPY webui /webui

RUN apk add --no-cache python3 py3-pip
RUN python3 -m venv .venv

# Установка зависимостей из requirements.txt первым шагом для лучшей кешируемости
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

# Установка самого пакета в editable режиме без зависимостей, так как они уже установлены
RUN .venv/bin/pip install -e . --no-deps

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
