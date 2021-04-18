#!/bin/bash

WSGI_FILE="url_shortener.wsgi:application"

status=1

# Run Celery in background
celery -A url_shortener worker -B -l info &

while [ $status -ne 0 ]; do
	gunicorn $WSGI_FILE --bind 0.0.0.0:$GUNICORN_BIND_PORT --workers=$GUNICORN_WORKERS
	status=$?
	sleep $GUNICORN_RETRY_DELAY
done