"""
Django settings for eye health project.

Generated by 'django-admin startproject' using Django 4.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from django.contrib.messages import constants as messages
import logging
from pathlib import Path
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_APPS = [
    "corsheaders",
    "rest_framework",
    "django.contrib.gis",
    "django_q",
]

LOCAL_APPS = [
    "api",
    "admin_panel",
    "store",
    "ai_doctor",
]

INSTALLED_APPS += THIRD_APPS + LOCAL_APPS
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOG_DIR = f"{BASE_DIR}/logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "django.log")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE,
            "maxBytes": 1024 * 1024 * 25,  # 25MB
            "backupCount": 5,
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Media files

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "api.UserModel"

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        hours=int(os.environ.get("ACCESS_TOKEN_LIFETIME_HOURS"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        hours=int(os.environ.get("REFRESH_TOKEN_LIFETIME_HOURS"))
    ),
    "ROTATE_REFRESH_TOKENS": True,
}


# SMTP
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# EYE TEST SERVER CONFIGURATION
EYE_TEST_BASE_API_URL = os.getenv("EYE_TEST_BASE_API_URL")
SNELLEN_FRACTION_STATIC_TOKEN = os.getenv("SNELLEN_FRACTION_STATIC_TOKEN")
EYE_TEST_DOMAIN_URL = os.getenv("EYE_TEST_DOMAIN_URL")

# EYE FATIGUE SERVER CONFIGURATION
FATIGUE_BASE_URL = os.getenv("FATIGUE_BASE_URL")
FATIGUE_DOMAIN_URL = os.getenv("FATIGUE_DOMAIN_URL")

# STRIP
STRIP_PUBLISHER_KEY = os.getenv("STRIP_PUBLISHER_KEY")
STRIP_SECRETS_KEY = os.getenv("STRIP_SECRETS_KEY")
STRIP_PAYMENT_SUCCESS_URL = os.getenv("STRIP_PAYMENT_SUCCESS_URL")
STRIP_PAYMENT_CANCEL_URL = os.getenv("STRIP_PAYMENT_CANCEL_URL")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# CBIS Configuration
CBIS_SMS_BASEURL = os.getenv("CBIS_SMS_BASEURL")
CBIS_SMS_USERNAME = os.getenv("CBIS_SMS_USERNAME")
CBIS_SMS_PASSWORD = os.getenv("CBIS_SMS_PASSWORD")
CBIS_SMS_SENDER_ID = os.getenv("CBIS_SMS_SENDER_ID")

# RAZOR PAY
RAZOR_PAY_KEY_ID = os.getenv("RAZOR_PAY_KEY_ID")
RAZOR_PAY_KEY_SECRET = os.getenv("RAZOR_PAY_KEY_SECRET")
RAZOR_PAY_WEBHOOK_SECRET = os.getenv("RAZOR_PAY_WEBHOOK_SECRET")

# logger = logging.getLogger("weasyprint")
# logger.addHandler(logging.FileHandler(os.path.join(LOG_DIR, "weasyprint.log")))


MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-error",
}
LOGIN_URL = "login_view"

DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # (50 MEGABYTES)


Q_CLUSTER = {
    "name": "DjangoQ",
    "workers": 4,
    "recycle": 500,
    "timeout": 60,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}
