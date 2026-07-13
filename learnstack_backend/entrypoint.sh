#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn --bind 0.0.0.0:8000 learnstack_backend.wsgi