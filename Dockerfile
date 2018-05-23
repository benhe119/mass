FROM python:3.6-jessie

ENV PYTHONUNBUFFERED 1

ENV PATH="/opt/bro/bin:${PATH}"

# TODO: set up supervisord to handle rqworker
RUN wget -qO - http://download.opensuse.org/repositories/network:/bro/Debian_8.0/Release.key | apt-key add - && \
    echo 'deb http://download.opensuse.org/repositories/network:/bro/Debian_8.0/ /' >> /etc/apt/sources.list.d/bro.list && \
    apt-get update && apt-get install -y bro && pip install bro-pkg

ADD . /app

WORKDIR /app/

RUN pip install -r requirements.txt
