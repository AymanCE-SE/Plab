# PLAB — Technical README

This document covers developer setup, tools, libraries, and operational notes to run and maintain PLAB locally and in production.

Contents

- Requirements
- Environment variables
- Local development
- Static files & media
- Translations
- Tests
- Deployment notes
- Useful commands

Requirements

- Python 3.10+ (use a virtual environment)
- PostgreSQL recommended for production (SQLite used by default in simple setups)
- The `requirements.txt` file pins the Python dependencies used by the project.

Environment variables

The project expects environment variables configured via a `.env` file. See `.env.example` for the complete list. Important variables:

- `SECRET_KEY` — keep secret in production
- `DEBUG` — set to `False` in production
- `ALLOWED_HOSTS` — list of hostnames (comma-separated)
- `DATABASE_URL` or standard `DATABASE_*` settings for production DB
- `STATIC_ROOT` and `MEDIA_ROOT` for collected static files and uploaded media

Local development setup

1. Create and activate a virtualenv

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS / Linux
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
# edit .env as needed (DEBUG=True for development)
```

4. Run database migrations and compile translations

```bash
python manage.py migrate
python manage.py compilemessages -l ar
```

5. Run the development server

```bash
python manage.py runserver
```

Static files and media

- During development static files are served by Django when `DEBUG=True`.
- In production, run:

```bash
python manage.py collectstatic --noinput
```

- Serve `MEDIA` (user uploads) from a proper media server or object storage (S3, etc.).
- The project is compatible with WhiteNoise for serving static files in simple deployments.

Translations

- The codebase includes Arabic translations. To update translations:

```bash
python manage.py makemessages -l ar
# edit the .po files in locale/ar/LC_MESSAGES/
python manage.py compilemessages -l ar
```

Testing

- If tests exist, run them with:

```bash
python manage.py test
```

Deployment notes

- See `DEPLOY.md` for platform-specific deployment steps and scripts.
- Recommended production stack: Gunicorn + Nginx (or a PaaS that hides the reverse proxy).
- Ensure `DEBUG=False`, proper `ALLOWED_HOSTS`, and HTTPS with HSTS.
- Use a robust database (Postgres) in production; SQLite is not recommended for production.

Useful commands

- Make migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`
- Run server: `python manage.py runserver`
- Collect static: `python manage.py collectstatic --noinput`
- Compile translations: `python manage.py compilemessages -l ar`

Troubleshooting

- If templates raise duplicate block errors, check `lab_core/templates/lab_core/base.html` and other templates for `{% block ... %}` duplicates.
- If static files are missing, verify `STATIC_ROOT`, run `collectstatic`, and inspect webserver configuration.

Contact

- For developer questions, open an issue or contact the maintainer listed in the project metadata.
