#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput --verbosity 0

# Start the uvicorn server
uvicorn project.asgi:application --host 0.0.0.0 --port 8000 --reload --app-dir=/backend
