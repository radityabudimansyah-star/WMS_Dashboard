web: cd wms_project/django_backend && python manage.py migrate && gunicorn --bind 0.0.0.0:$PORT --pythonpath . wsgi:application
