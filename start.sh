#!/bin/bash
cd /app/wms_project/django_backend
python manage.py migrate
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application
