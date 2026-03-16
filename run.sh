#!/bin/bash
if [ "$SERVICE_TYPE" = "frontend" ]; then
  echo "Starting Streamlit frontend..."
  python -m streamlit run wms_project/streamlit_frontend/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
else
  echo "Starting Django backend..."
  python wms_project/django_backend/manage.py migrate
  gunicorn --bind 0.0.0.0:$PORT wsgi:application
fi
