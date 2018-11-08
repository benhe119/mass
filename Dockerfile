FROM python:3.6-slim-jessie

ENV PYTHONUNBUFFERED 1

ENV PATH="/opt/bro/bin:${PATH}"

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /app/

COPY etc/apt/Release.key etc/apt/Release.key

COPY requirements/base.txt requirements/base.txt

RUN pip install pip --upgrade && \
    pip install -r requirements/base.txt bro-pkg

RUN apt-key add etc/apt/Release.key && \
    echo 'deb http://download.opensuse.org/repositories/network:/bro/Debian_8.0/ /' >> /etc/apt/sources.list.d/bro.list && \
    apt-get update && apt-get install -y bro curl supervisor p7zip-full clamav-daemon clamdscan netcat-openbsd nginx

RUN mkdir -p /etc/supervisor/conf.d/

COPY etc/supervisord/conf.d/* /etc/supervisor/conf.d/

COPY etc/nginx/nginx.conf /etc/nginx/nginx.conf
