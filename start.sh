#!/bin/bash
set -e
echo "Current directory: $(pwd)"
echo "Files in current dir:"
ls -la
echo "Looking for django_backend..."
find . -name "manage.py" 2>/dev/null
DJANGO_DIR=$(find . -name "manage.py" | head -1 | xargs dirname)
echo "Found Django at: $DJANGO_DIR"
cd $DJANGO_DIR
echo "Now in: $(pwd)"
python manage.py migrate
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application
