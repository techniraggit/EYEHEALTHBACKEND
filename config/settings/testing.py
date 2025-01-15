from .base import *
import json

DEBUG = True

ALLOWED_HOSTS = json.loads(os.environ.get("ALLOWED_HOSTS", "[]"))
CORS_ALLOW_HEADERS = json.loads(os.environ.get("CORS_ALLOW_HEADERS", "[]"))
CSRF_TRUSTED_ORIGINS = json.loads(os.environ.get("CSRF_TRUSTED_ORIGINS", "[]"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    }
}
