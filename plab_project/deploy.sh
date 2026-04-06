#!/usr/bin/env bash
# PLAB — run on the server from the project root (folder that contains manage.py).
# Usage: chmod +x deploy.sh && ./deploy.sh
# Ensure `.env` is present and gettext (`msgfmt`) is installed for compilemessages.

set -euo pipefail
cd "$(dirname "$0")"

if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source ".venv/bin/activate"
fi

echo "==> pip install"
python -m pip install -r requirements.txt

echo "==> migrate"
python manage.py migrate --noinput

echo "==> collectstatic"
python manage.py collectstatic --noinput

echo "==> compilemessages (Arabic)"
python manage.py compilemessages -l ar

echo "==> Done. Restart Gunicorn / your WSGI process if needed."
