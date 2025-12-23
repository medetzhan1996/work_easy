import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SECRET_KEY = "*+uiasgfhfhea(0_=n@c6aacvxcd*xtaassdkjlgvzo"

DEBUG = True

ALLOWED_HOSTS = ["*"]

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'postgres',
#         'USER': 'postgres',
#         'PASSWORD': 'postgres',
#         'HOST': 'localhost',
#         'PORT': '5432'
#     }
# }
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_DIR = os.path.join(BASE_DIR, "static")

# STATICFILES_DIRS is a list of locations where Django will look for additional static files
STATICFILES_DIRS = [
    STATIC_DIR,  # Add your custom directory for static files
]

# STATIC_ROOT is where all static files will be collected to when running collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
CSRF_TRUSTED_ORIGINS = ["http://185.22.65.58"]
