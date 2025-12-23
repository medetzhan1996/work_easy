#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

#python manage.py makemigrations allauth # WHY THEY DONT HAVE MIGRATION IN THEIR REPOSITORY???
#python manage.py migrate
python manage.py collectstatic --noinput --verbosity 0
daphne -b 0.0.0.0 -p 8000 project.asgi:application
