#!/bin/bash

pip install flake8 coverage fakeredis
export DJANGO_SETTINGS_MODULE=mass.settings.devel
find {filestore,mass} -name "__pycache__" | xargs rm -rf
rm -rf mass/db.sqlite3
rm -rf files/*
rm -rf */migrations/*
rm -rf static/*
cp etc/clamav/*.cvd /var/lib/clamav/
chown -R clamav:clamav /var/lib/clamav
python manage.py makemigrations filestore
python manage.py migrate
freshclam
/etc/init.d/clamav-daemon start
rm -rf debug.log
python manage.py loaddata init_data.json
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
