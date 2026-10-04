#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python -c "import os; print('CLOUD_NAME:', os.environ.get('CLOUDINARY_CLOUD_NAME')); print('API_KEY present:', bool(os.environ.get('CLOUDINARY_API_KEY'))); print('API_SECRET present:', bool(os.environ.get('CLOUDINARY_API_SECRET')))"
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsuperuser --noinput || true