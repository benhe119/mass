FROM python:3.6-jessie

ENV PYTHONUNBUFFERED 1

ENV PATH="/opt/bro/bin:${PATH}"

RUN wget -qO - http://download.opensuse.org/repositories/network:/bro/Debian_8.0/Release.key | apt-key add - && \
    echo 'deb http://download.opensuse.org/repositories/network:/bro/Debian_8.0/ /' >> /etc/apt/sources.list.d/bro.list && \
    apt-get update && apt-get install -y bro && pip install bro-pkg

ADD . /app

WORKDIR /app/

RUN mkdir -p /var/lib/bro

RUN pip install -r requirements.txt
