#!/bin/bash
set -e
DJANGO_DIR=/app/wms_project/django_backend
python $DJANGO_DIR/manage.py migrate --pythonpath $DJANGO_DIR --settings settings
exec gunicorn --bind 0.0.0.0:$PORT --pythonpath $DJANGO_DIR wsgi:application
