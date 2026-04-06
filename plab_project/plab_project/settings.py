"""
Django settings for plab_project.

Loads local overrides from a `.env` file in the project root (next to `manage.py`)
via python-dotenv. See `.env.example` for variables.
"""

from pathlib import Path
import os
import dj_database_url

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _get_list(name: str, default: tuple[str, ...] | None = None) -> list[str]:
    raw = os.getenv(name, "")
    if not raw.strip():
        return list(default) if default is not None else []
    return [x.strip() for x in raw.split(",") if x.strip()]


def _env_str(key: str, default: str = "") -> str:
    if key not in os.environ:
        return default
    return os.environ[key].strip()


DEBUG = _get_bool("DEBUG", default=True)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-dev-only-replace-with-real-key"
    else:
        raise ImproperlyConfigured("SECRET_KEY must be set in the environment when DEBUG is False.")

ALLOWED_HOSTS = _get_list("ALLOWED_HOSTS")
if not ALLOWED_HOSTS and not DEBUG:
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set when DEBUG is False.")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "cloudinary_storage",
    "django.contrib.staticfiles",
    "lab_core",
    "cloudinary"
]

AUTH_USER_MODEL = "lab_core.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "plab_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "lab_core.context_processors.lab_announcements",
            ],
        },
    },
]

WSGI_APPLICATION = "plab_project.wsgi.application"

_sqlite_name = _env_str("SQLITE_PATH", "db.sqlite3")
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": Path(_sqlite_name) if Path(_sqlite_name).is_absolute() else BASE_DIR / _sqlite_name,
#     }
# }

# --- Database Configuration ---
# سيحاول النظام القراءة من DATABASE_URL (لـ Postgres)، وإذا لم يجدها سيستخدم SQLite محلياً
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / _env_str('SQLITE_PATH', 'db.sqlite3')}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ar"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("ar", _("Arabic")),
    ("en", _("English")),
]

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

def _url_with_trailing_slash(url: str, default: str) -> str:
    u = (url or default).strip()
    return u if u.endswith("/") else u + "/"

# --- Cloudinary & Static/Media ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# إذا وجدت بيانات Cloudinary، سيتم استخدامها للميديا
if CLOUDINARY_STORAGE['CLOUD_NAME']:
    _media_backend = 'cloudinary_storage.storage.RawMediaCloudinaryStorage'
else:
    _media_backend = 'django.core.files.storage.FileSystemStorage'

# STATIC_URL = _url_with_trailing_slash(os.getenv("STATIC_URL"), "static/")
# STATIC_ROOT = BASE_DIR / _env_str("STATIC_ROOT_DIR", "staticfiles")
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / _env_str("STATIC_ROOT_DIR", "staticfiles")

# MEDIA_URL = _url_with_trailing_slash(os.getenv("MEDIA_URL"), "/media/")
# MEDIA_ROOT = BASE_DIR / _env_str("MEDIA_ROOT_DIR", "media")
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / _env_str("MEDIA_ROOT_DIR", "media")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
# Manifest storage requires `collectstatic`; use plain storage in DEBUG for smoother local dev.
_staticfiles_backend = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
    if DEBUG
    else "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

STORAGES = {
    "default": {
        "BACKEND": _media_backend,
    },
    "staticfiles": {
        "BACKEND": _staticfiles_backend,
    },
}

LOGIN_URL = "lab_core:login"
LOGIN_REDIRECT_URL = "lab_core:dashboard"
LOGOUT_REDIRECT_URL = "lab_core:login"

# --- About page (env overrides; if key omitted from .env, defaults below apply) ---
PLAB_ABOUT_DESCRIPTION = _env_str(
    "PLAB_ABOUT_DESCRIPTION",
    "Medical Chemical Analysis Laboratory - Always with you because you deserve the best",
)
PLAB_ABOUT_DESCRIPTION_AR = _env_str(
    "PLAB_ABOUT_DESCRIPTION_AR",
    "معمل التحاليل الطبيه الكيميائية - دائما معك لانك تستحق الافضل",
)
PLAB_ABOUT_PHONE = _env_str("PLAB_ABOUT_PHONE", "01273512252 - 01202266850")
PLAB_ABOUT_ADDRESS = _env_str(
    "PLAB_ABOUT_ADDRESS",
    "AbuHammad - Sharkya front of police station bridge Above Al-Tawhid Wal-Nur - Fifth Floor",
)
PLAB_ABOUT_ADDRESS_AR = _env_str(
    "PLAB_ABOUT_ADDRESS_AR",
    "ابوsssحماد - الشرقيه امام كوبري المركز اعلي التوحيد والنور - الدور الخامس",
)
PLAB_ABOUT_HOURS = _env_str("PLAB_ABOUT_HOURS", "Open 7 days a week: 10:00 AM – 12:00 AM")
PLAB_ABOUT_HOURS_AR = _env_str("PLAB_ABOUT_HOURS_AR", "طوال ايام الاسبوع: ١٠ ص – ١٢ ص")
PLAB_MAP_EMBED_URL = _env_str(
    "PLAB_MAP_EMBED_URL",
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d214.78763152826744!2d31.67282783324484!3d30.532288431757497!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x14f81c87f679baf3%3A0x9f1f003e86d777ee!2sAbu%20Hammad%2C%20Kafr%20Al%20Azzazi%2C%20Abu%20Hammad%2C%20Al-Sharqia%20Governorate!5e0!3m2!1sen!2seg!4v1775297659513!5m2!1sen!2seg",
)

# --- Production security ---
if not DEBUG:
    SESSION_COOKIE_SECURE = _get_bool("SESSION_COOKIE_SECURE", default=True)
    CSRF_COOKIE_SECURE = _get_bool("CSRF_COOKIE_SECURE", default=True)
    SECURE_SSL_REDIRECT = _get_bool("SECURE_SSL_REDIRECT", default=True)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    if SECURE_HSTS_SECONDS > 0:
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "DENY"

_csrf_origins = _get_list("CSRF_TRUSTED_ORIGINS")
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = _csrf_origins
