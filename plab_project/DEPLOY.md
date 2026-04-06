# PLAB — deployment command checklist

Run these **from the Django project root** (the folder that contains `manage.py` and `.env`), after activating your virtualenv if you use one.

## One-liner (Linux / macOS)

```bash
chmod +x deploy.sh && ./deploy.sh
```

## Manual checklist (same steps)

| Step | Command |
|------|---------|
| 1. Dependencies | `python -m pip install -r requirements.txt` |
| 2. Database | `python manage.py migrate --noinput` |
| 3. Static files | `python manage.py collectstatic --noinput` |
| 4. Translations | `python manage.py compilemessages -l ar` |
| 5. Restart | Restart **Gunicorn** (or your WSGI service) so workers load new code. |

## Windows (PowerShell)

```powershell
.\deploy.ps1
```

Or run the same five steps manually using `py` instead of `python` if that is how you invoke Python.

## Notes

- **`.env`** must exist beside `manage.py` (same folder as `.env.example`) with production values (`DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS`, etc.).
- **`compilemessages`** needs GNU **gettext** (`msgfmt`) on the server. If it is missing, install the `gettext` package for your OS, or compile messages on a dev machine and deploy the `locale/**/django.mo` files.
- After deploy, serve **media** (`MEDIA_ROOT`) via nginx or equivalent; Django does not serve uploads like in `DEBUG` mode.
