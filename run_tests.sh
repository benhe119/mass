#!/bin/bash

pip install -r requirements/test.txt 
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
python -m flake8 --max-line-length=119 filestore/ mass/
rm -rf debug.log
python -m coverage run --source=filestore --omit=filestore/tests/test_*.py,filestore/migrations/* manage.py test filestore/tests -v 2
python -m coverage report -m
