#!/usr/bin/env bash
set -euo pipefail
echo "==> Installing dependencies"
pip install --upgrade pip # this is optional
pip install -r requirements.txt
# Ensure gunicorn is installed (some build environments ignore requirements)
pip install --no-cache-dir gunicorn
echo "==> Running database migrations"
python manage.py makemigrations
python manage.py migrate --noinput
echo "==> Collecting static files"
python manage.py collectstatic --noinput
echo "==> Build complete"