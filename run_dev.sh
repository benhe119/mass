#!/bin/bash

pip install fakeredis django-debug-toolbar
export DJANGO_SETTINGS_MODULE=mass.settings.devel
find {filestore,mass} -name "__pycache__" | xargs rm -rf
rm -rf mass/db.sqlite3
rm -rf files/*
rm -rf */migrations/*
cp etc/clamav/*.cvd /var/lib/clamav/
chown -R clamav:clamav /var/lib/clamav
python manage.py makemigrations filestore debug_toolbar
python manage.py migrate
freshclam
/etc/init.d/clamav-daemon start
rm -rf debug.log
python manage.py loaddata init_data.json
curl -s -o /dev/null -w "%{http_code}" -L http://localhost:8000/update_clamav_db
python manage.py runserver 0.0.0.0:8000
