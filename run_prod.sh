#!/usr/bin/env bash
export DJANGO_SETTINGS_MODULE=mass.settings.prod
service supervisor start
rm -rf mass/db.sqlite3
rm -rf files/*
rm -rf */migrations/*
rm -rf static/*
cp etc/clamav/*.cvd /var/lib/clamav/
chown -R clamav:clamav /var/lib/clamav
python manage.py makemigrations
python manage.py migrate --run-syncdb
freshclam
/etc/init.d/clamav-daemon start
python manage.py loaddata init_data.json
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
