import os
from pathlib import Path
import django_heroku
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-^+e$ae-he)jy#6e0d(h*+0-c=*j9%)v_a$z6y#-6qxsxuq&ydb'

DEBUG = True

ALLOWED_HOSTS = ['mamamaasaibakers.com' ]

INSTALLED_APPS = [
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'category',
    'accounts',
    'store',
    'carts',
    'orders',
    'admin_thumbnails',
    'finance',
    'storages',
    'CDMIS',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_EXPIRE_SECONDS = 3600  # 1 hour
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = 'accounts/login'


ROOT_URLCONF = 'beststore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.menu_links',
                'carts.context_processors.counter',
            ],
        },
    },
]

WSGI_APPLICATION = 'beststore.wsgi.application'

AUTH_USER_MODEL = 'accounts.Account'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]




# Use Bucketeer environment variables
BUCKETEER_BUCKET_NAME = os.environ.get('BUCKETEER_BUCKET_NAME')
BUCKETEER_AWS_ACCESS_KEY_ID = os.environ.get('BUCKETEER_AWS_ACCESS_KEY_ID')
BUCKETEER_AWS_SECRET_ACCESS_KEY = os.environ.get('BUCKETEER_AWS_SECRET_ACCESS_KEY')
BUCKETEER_REGION = os.environ.get('BUCKETEER_AWS_REGION', 'us-east-1')

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = BUCKETEER_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = BUCKETEER_AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = BUCKETEER_BUCKET_NAME
AWS_S3_REGION_NAME = BUCKETEER_REGION
AWS_QUERYSTRING_AUTH = False  # Optional: makes URLs more readable
MEDIA_URL = f'https://{BUCKETEER_BUCKET_NAME}.s3.amazonaws.com/'





LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images, APKs)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Place your apk file in static/apk/
]
STATIC_ROOT = BASE_DIR / "staticfiles"


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (user-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mamamaassaibakers@gmail.com'
EMAIL_HOST_PASSWORD = 'ujqc yeoo sagb zajx'
DEFAULT_FROM_EMAIL = 'mamamaassaibakers@gmail.com'

# Heroku static files support
django_heroku.settings(locals())