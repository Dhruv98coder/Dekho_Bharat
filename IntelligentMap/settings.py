"""
Django settings for IntelligentMap project.

GoPlan - Django Only Integrated Application
"""

from pathlib import Path
import os


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-local-only-change-me",
)

DEBUG = os.getenv("DEBUG", "True").lower() == "true"


# ============================================================
# ALLOWED HOSTS
# ============================================================
#
# Local:
#   127.0.0.1
#   localhost
#
# Render:
#   dekho-bharat.onrender.com
#
# Render environment variable can override this.
# Example:
# ALLOWED_HOSTS=dekho-bharat.onrender.com
# ============================================================

_default_hosts = (
    "127.0.0.1,"
    "localhost,"
    "dekho-bharat.onrender.com"
)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        _default_hosts,
    ).split(",")
    if host.strip()
]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    # --------------------------------------------------------
    # Django
    # --------------------------------------------------------
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # --------------------------------------------------------
    # GoPlan modules
    # --------------------------------------------------------
    "goplan_home",
    "map_engine",
    "native_language",
    "metro",
    "chatbot",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise for static files on Render
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL / WSGI
# ============================================================

ROOT_URLCONF = "IntelligentMap.urls"

WSGI_APPLICATION = "IntelligentMap.wsgi.application"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ============================================================
# DATABASE
# ============================================================
#
# Current setup:
# SQLite only
#
# No PostgreSQL required right now.
# No dj_database_url required.
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ============================================================
# CSRF
# ============================================================
#
# Render:
# https://dekho-bharat.onrender.com
#
# The environment variable can still be overridden later.
# ============================================================

_default_csrf_origins = (
    "http://127.0.0.1:8000,"
    "http://localhost:8000,"
    "https://dekho-bharat.onrender.com"
)

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        _default_csrf_origins,
    ).split(",")
    if origin.strip()
]


# ============================================================
# HTTPS / PROXY
# ============================================================

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

# Main project static directory
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Production collected static directory
STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# STATIC STORAGE / WHITENOISE
# ============================================================

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },

    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# AI CONFIGURATION
# ============================================================

# Possible providers:
#   rule_based
#   local_model
#   openai
#   future_model
#
# The default keeps the application lightweight.

AI_PROVIDER = os.getenv(
    "AI_PROVIDER",
    "rule_based",
)


# ============================================================
# GOPLAN MODULE FLAGS
# ============================================================

GOPLAN_APP_NAME = "GoPlan"

INTELLIGENT_MAP_ENABLED = True

NATIVE_LANGUAGE_ENABLED = True

METRO_ENABLED = True

SHRISTI_ENABLED = True


# ============================================================
# ROUTING CONFIGURATION
# ============================================================

ORS_API_KEY = os.getenv(
    "ORS_API_KEY",
    "",
)

GOPLAN_BIKE_ROUTER_URL = os.getenv(
    "GOPLAN_BIKE_ROUTER_URL",
    "https://routing.openstreetmap.de/routed-bike/route/v1/driving",
)

GOPLAN_FOOT_ROUTER_URL = os.getenv(
    "GOPLAN_FOOT_ROUTER_URL",
    "https://routing.openstreetmap.de/routed-foot/route/v1/driving",
)

try:
    GOPLAN_ROUTER_TIMEOUT = int(
        os.getenv(
            "GOPLAN_ROUTER_TIMEOUT",
            "25",
        )
    )
except ValueError:
    GOPLAN_ROUTER_TIMEOUT = 25


# ============================================================
# FILE UPLOAD LIMITS
# ============================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024


# ============================================================
# PRODUCTION SECURITY
# ============================================================

# Enable secure cookies only when DEBUG=False.
SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_SECURE = not DEBUG

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True


# ============================================================
# OPTIONAL RENDER SETTINGS
# ============================================================

# Keep this False unless you specifically want Django to
# redirect HTTP requests to HTTPS.

SECURE_SSL_REDIRECT = False