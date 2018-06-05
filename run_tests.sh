#!/bin/bash

# python manage.py makemigrations filestore
# python manage.py migrate
export DJANGO_SETTINGS_MODULE=mass.settings.test
python -m flake8 filestore/ mass/
rm -rf debug.log
python -m coverage run --source=filestore --omit=filestore/tests/test_*.py,filestore/migrations/* manage.py test filestore/tests -v 2
python -m coverage report -m

