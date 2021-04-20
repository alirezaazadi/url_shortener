#!/bin/bash

WSGI_FILE="url_shortener.wsgi:application"

status=1

python manage.py collectstatic --no-input
python manage.py migrate --no-input --skip-checks
python manage.py createsuperuser --username $DJANGO_SUPERUSER_USERNAME --email a@a.com --no-input
python manage.py initdatabase

# Run Celery in background
celery -A url_shortener worker -B -l info &

while [ $status -ne 0 ]; do
	gunicorn $WSGI_FILE --bind 0.0.0.0:$GUNICORN_BIND_PORT --workers=$GUNICORN_WORKERS
	status=$?
	sleep $GUNICORN_RETRY_DELAY
done