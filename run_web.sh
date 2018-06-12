#!/usr/bin/env bash
export DJANGO_SETTINGS_MODULE=mass.settings.devel
find {filestore,mass} -name "__pycache__" | xargs rm -rf
rm -rf mass/db.sqlite3
rm -rf files/*
rm -rf */migrations/*
rm -rf static/*
python manage.py makemigrations
python manage.py migrate --run-syncdb
python manage.py loaddata init_data.json
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
