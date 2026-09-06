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


ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if host.strip()
]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # GoPlan modules
    "map_engine",
    "metro",
    "goplan_home",
    "chatbot",
    "native_language",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    # Security
    "django.middleware.security.SecurityMiddleware",

    # Static files / production support
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # Django
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

        # Main project templates folder
        "DIRS": [
            BASE_DIR / "templates",
        ],

        # Also search templates inside Django apps
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
# Local development uses SQLite only.
#
# No PostgreSQL
# No DATABASE_URL
# No dj_database_url
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

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "",
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
#
# Project structure:
#
# GoPlan/
# ├── static/
# │   ├── css/
# │   │   └── app_shell.css
# │   ├── js/
# │   └── images/
# │
# └── staticfiles/
#
# ============================================================

STATIC_URL = "/static/"


# Source static directory
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# Production collectstatic output
STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# STATIC STORAGE
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

# Current AI provider.
#
# Example:
# rule_based
# future_model
# openai
# local_model
#
# This allows the AI implementation to be changed later
# without changing the whole application.
AI_PROVIDER = os.getenv(
    "AI_PROVIDER",
    "rule_based",
)


# ============================================================
# GO PLAN APPLICATION SETTINGS
# ============================================================

# Main application name
GOPLAN_APP_NAME = "GoPlan"

# Native Language module
NATIVE_LANGUAGE_ENABLED = True

# Intelligent Map module
INTELLIGENT_MAP_ENABLED = True

# Metro module
METRO_ENABLED = True

# Shristi AI assistant
SHRISTI_ENABLED = True


# ============================================================
# DEVELOPMENT
# ============================================================

# Useful during local development
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024