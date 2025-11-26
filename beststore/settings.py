import os
from pathlib import Path
import django_heroku
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from django.contrib.messages import constants as messages

# ========================= BASE DIRECTORY =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================= SECRET KEY =========================
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-kds8lcf_2yb3w_!l!qn=k(tc6^y_%4*nbsw5h62)_t8%4((a-4')

# ========================= DEBUG MODE =========================
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ========================= ALLOWED HOSTS =========================
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'mamamaasaibakers.com').split(',')

# ========================= INSTALLED APPS =========================
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
    'cloudinary',
    'cloudinary_storage',
    'school',
]

# ========================= JAZZMIN SETTINGS =========================
JAZZMIN_SETTINGS = {
    "site_title": "Mama Maasai Bakers Admin",
    "site_header": "Mama Maasai Bakers",
    "site_brand": "Mama Maasai Bakers",
    "welcome_sign": "Welcome to Mama Maasai Bakers Admin Dashboard",
    "copyright": "Mama Maasai Bakers",
    "search_model": ["accounts.Account", "store.Product", "category.Category"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["accounts", "store", "category", "orders", "CDMIS", "finance"],
    "custom_links": {
        "accounts": [
            {
                "name": "View Site",
                "url": "https://mamamaasaibakers.com",
                "icon": "fas fa-globe",
                "new_window": True
            },
            {
                "name": "Visit CDMIS",
                "url": "https://mamamaasaibakers.com/cdmis/groups",
                "icon": "fas fa-users",
                "new_window": True
            }
        ]
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

# ========================= SESSION CONFIGURATION =========================
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 2592000  # 30 days
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ========================= CACHE CONFIGURATION =========================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# ========================= CSRF CONFIGURATION =========================
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_AGE = 31449600  # 1 year

# ========================= MIDDLEWARE =========================
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

# ========================= DATABASE CONFIGURATION =========================
DATABASE_URL = os.environ.get('DATABASE_URL')

if DEBUG or not DATABASE_URL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'ATOMIC_REQUESTS': True,
            'CONN_MAX_AGE': 600,
        }
    }
else:
    parsed_db = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        atomic_requests=True,
    )
    if not parsed_db.get('ENGINE'):
        raise ImproperlyConfigured("DATABASE_URL parsing failed - no ENGINE found")
    parsed_db['OPTIONS'] = {
        'sslmode': 'require',
        'connect_timeout': 10,
    }
    DATABASES = {'default': parsed_db}

# ========================= CLOUDINARY STORAGE =========================
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

if not DEBUG:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# ========================= EMAIL CONFIGURATION =========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# ========================= PASSWORD VALIDATION =========================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ========================= INTERNATIONALIZATION =========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# ========================= STATIC FILES =========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ========================= MESSAGES =========================
MESSAGE_TAGS = {
    messages.SUCCESS: 'success',
    messages.ERROR: 'danger',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========================= SECURITY SETTINGS =========================
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
X_FRAME_OPTIONS = 'DENY'

# ========================= HEROKU/RENDER CONFIGURATION =========================
if not DEBUG:
    try:
        django_heroku.settings(locals())
    except Exception as e:
        print(f"⚠️ django_heroku warning: {e}")