FROM python:3.6-slim-jessie

ENV PYTHONUNBUFFERED 1

ENV PATH="/opt/bro/bin:${PATH}"

ENV DEBIAN_FRONTEND noninteractive

COPY etc/apt/Release.key etc/apt/Release.key

RUN apt-key add etc/apt/Release.key && \
    echo 'deb http://download.opensuse.org/repositories/network:/bro/Debian_8.0/ /' >> /etc/apt/sources.list.d/bro.list && \
    apt-get update && apt-get install -y bro supervisor p7zip-full clamav-daemon clamdscan netcat-openbsd

COPY . /app

WORKDIR /app/

RUN pip install -r requirements/base.txt bro-pkg

RUN useradd -s /bin/bash django_rq && \
    mkdir -p /etc/supervisor/conf.d/ && \
    cp /app/django_rq.conf /etc/supervisor/conf.d/
