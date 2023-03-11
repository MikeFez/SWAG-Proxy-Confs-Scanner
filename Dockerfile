FROM python:3.8-slim-buster

LABEL maintainer="Michael Fessenden <michael@mikefez.com>"

ADD swag_proxy_confs_scanner /opt/app

RUN python3 -m venv /opt/app/.venv && \
    /opt/app/.venv/bin/pip install --no-cache-dir -r /opt/app/requirements.txt

ENTRYPOINT ["/bin/sh", "-c", "\
    if [ ! -d '/proxy-confs' ]; then \
        echo '/proxy-confs directory was not mounted!'; \
    else \
        /opt/app/.venv/bin/python3 /opt/app/app.py; \
    fi"]