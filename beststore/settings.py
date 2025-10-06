import os
from pathlib import Path
import django_heroku
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-^+e$ae-he)jy#6e0d(h*+0-c=*j9%)v_a$z6y#-6qxsxuq&ydb')

DEBUG = False

ALLOWED_HOSTS = ['mamamaasaibakers.com']

INSTALLED_APPS = [
    'jazzmin',
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
    'cloudinary_storage',
    'cloudinary',
]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'dhklmtpxy'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '345437392578237'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'Vz5iaCXqJlNOO3oCQ-41J-tsVbA'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

JAZZMIN_SETTINGS = {
    "site_title": "Mama Maasai Bakers Admin",
    "site_header": "Mama Maasai Bakers",
    "site_brand": "Mama Maasai Bakers",
    "welcome_sign": "Welcome to Mama Maasai Bakers Admin",
    "copyright": "Mama Maasai Bakers © 2025",
    "search_model": ["accounts.Account", "store.Product", "orders.Order"],
    "user_avatar": "accounts/static/images/logo.png",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["accounts", "store", "orders", "finance", "CDMIS"],
    "custom_links": {
        "accounts": [{
            "name": "User Guide",
            "url": "https://mamamaasaibakers.com/help/",
            "icon": "fas fa-book",
            "target": "_blank",
        }]
    },
    "icons": {
        "accounts.Account": "fas fa-user",
        "store.Product": "fas fa-bread-slice",
        "orders.Order": "fas fa-shopping-cart",
        "finance.Payment": "fas fa-money-bill-wave",
        "CDMIS.Group": "fas fa-users",
        "CDMIS.Member": "fas fa-user-friends",
    },
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "accounts.Account": "single",
        "store.Product": "collapsible",
    },
    "show_ui_builder": True,
    "theme": "green",
    "custom_css": None,
    "custom_js": None,
}

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

# Use Postgres on Heroku, fallback to SQLite locally
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }
else:
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'mamamaassaibakers@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'ujqc yeoo sagb zajx')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'mamamaassaibakers@gmail.com')

django_heroku.settings(locals())