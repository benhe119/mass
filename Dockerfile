FROM python:3.6-jessie

ENV PYTHONUNBUFFERED 1

ENV PATH="/opt/bro/bin:${PATH}"

RUN wget -qO - http://download.opensuse.org/repositories/network:/bro/Debian_8.0/Release.key | apt-key add - && \
    echo 'deb http://download.opensuse.org/repositories/network:/bro/Debian_8.0/ /' >> /etc/apt/sources.list.d/bro.list && \
    apt-get update && apt-get install -y bro supervisor p7zip && pip install bro-pkg

COPY . /app

WORKDIR /app/

RUN pip install -r requirements.txt

RUN useradd -s /bin/bash django_rq && \
    mkdir -p /etc/supervisor/conf.d/ && \
    cp /app/django_rq.conf /etc/supervisor/conf.d/
