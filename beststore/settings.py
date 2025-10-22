import os
from pathlib import Path
import django_heroku
import dj_database_url
import cloudinary_storage

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-kds8lcf_2yb3w_!l!qn=k(tc6^y_%4*nbsw5h62)_t8%4((a-4')
DEBUG = True
ALLOWED_HOSTS = ['mamamaasaibakers.onrender.com', 'mamamaasaibakers.com']

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

JAZZMIN_SETTINGS = {
    "site_title": "Mama Maasai Bakers Admin",
    "site_header": "Mama Maasai Bakers",
    "site_brand": "Mama Maasai Bakers",
    "welcome_sign": "Welcome to Mama Maasai Bakers Admin Dashboard",
    "copyright": "Mama Maasai Bakers",
    "search_model": ["accounts.Account", "store.Product", "category.Category"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["accounts", "store", "category", "orders", "CDMIS", "finance"],
    "custom_links": {
        "accounts": [{
            "name": "View Site",
            "url": "https://mamamaasaibakers.com",
            "icon": "fas fa-globe",
            "new_window": True
        }, {
            "name": "visit CDMIS",
            "url": "https://mamamaasaibakers.com/cdmis/groups",
            "icon": "fas fa-users",
            "new_window": True

        }]
    },
    "icons": {
        "accounts.Account": "fas fa-user",
        "store.Product": "fas fa-bread-slice",
        "category.Category": "fas fa-list",
        "orders.Order": "fas fa-shopping-cart",
        "CDMIS.Group": "fas fa-users",
        "finance.Payment": "fas fa-money-bill-wave",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "accounts.Account": "single",
        "store.Product": "collapsible",
        "category.Category": "vertical_tabs",
        "orders.Order": "horizontal_tabs",
        "CDMIS.Group": "collapsible",
        "finance.Payment": "horizontal_tabs",
        
    },
}

SESSION_COOKIE_AGE = 2400  # 40 minutes in seconds
SESSION_SAVE_EVERY_REQUEST = True

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

ROOT_URLCONF = 'beststore.urls'

LOGIN_REDIRECT_URL = 'redirect_after_login'

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
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://postgres:password@localhost:5432/postgres',  # Fallback for local development
        conn_max_age=600,
    )
}
# postgresql://beststore_django_render_user:jg79k7m3AvDtfKKfXcdHOwQa9QyLEF6F@dpg-d3sckm3e5dus73e162vg-a.oregon-postgres.render.com/beststore_django_render
# Cloudinary storage for media files
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dhklmtpxy',
    'API_KEY': '345437392578237',
    'API_SECRET': 'Vz5iaCXqJlNOO3oCQ-41J-tsVbA',
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'mamamaassaibakers@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'ujqc yeoo sagb zajx')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'mamamaassaibakers@gmail.com')

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Main static directory
]
STATIC_ROOT = BASE_DIR / "staticfiles"  # Directory for collected static files

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

django_heroku.settings(locals())