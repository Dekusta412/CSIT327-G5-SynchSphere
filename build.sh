#!/usr/bin/env bash
set -euo pipefail
echo "==> Installing dependencies"
pip install --upgrade pip # this is optional
pip install -r requirements.txt
# Ensure gunicorn is installed (some build environments ignore requirements)
pip install --no-cache-dir gunicorn
# Ensure whitenoise is installed so Django can import it at runtime
pip install --no-cache-dir whitenoise
echo "==> Running database migrations"
python manage.py makemigrations
python manage.py migrate --noinput
echo "==> Collecting static files"
python manage.py collectstatic --noinput
echo "==> Creating media directories"
mkdir -p media/avatars
chmod -R 755 media
echo "==> Build complete"