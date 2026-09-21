# #!/usr/bin/env bash
# set -o errexit
# pip install -r requirements.txt
# python manage.py collectstatic --no-input
# python manage.py migrate
# python manage.py createsuperuser --noinput || true


#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
echo "Contents of project root:"
ls -la
echo "Looking for static folder:"
ls -la static || echo "static folder NOT FOUND at this path"
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsuperuser --noinput || true