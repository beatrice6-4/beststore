import os
from pathlib import Path
import django_heroku
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-kds8lcf_2yb3w_!l!qn=k(tc6^y_%4*nbsw5h62)_t8%4((a-4')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['mamamaasaibakers.com', 'localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Add this for sites framework
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
]

# Sites Framework Configuration
SITE_ID = 1

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

SESSION_COOKIE_AGE = 2400
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

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
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

# ========================= DATABASE CONFIGURATION =========================

# LOCAL DEVELOPMENT - SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ========================= CLOUDINARY CONFIGURATION =========================

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'df44dwnwg',
    'API_KEY': '626193889524544',
    'API_SECRET': 'r40hH_tPzZ8BRQKaTKnb-2ZdAfU',
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/'

# ========================= EMAIL CONFIGURATION =========================
# Configure email for OTP sending

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# For Gmail: Use App-Specific Passwords
# 1. Enable 2-Factor Authentication on your Google Account
# 2. Go to myaccount.google.com/apppasswords
# 3. Create an app password for Django
# 4. Use that password below

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'mamamaassaibakers@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'ujqc yeoo sagb zajx')  # Gmail App Password
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'mamamaassaibakers@gmail.com')

# Email configuration timeout
EMAIL_TIMEOUT = 10

# For production, add these:
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_SSL = False
    EMAIL_USE_TLS = True

# ========================= CACHE CONFIGURATION =========================
# Cache for storing OTP temporarily

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'beststore-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# For production with Redis (optional):
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'CONNECTION_POOL_KWARGS': {'max_connections': 50}
#         }
#     }
# }

# ========================= SESSION CONFIGURATION =========================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = not DEBUG  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = True

# ========================= OTP CONFIGURATION =========================

# OTP Settings for Password Reset
OTP_LENGTH = 6
OTP_EXPIRY_TIME = 600  # 10 minutes in seconds
OTP_MAX_ATTEMPTS = 5
OTP_RESEND_COOLDOWN = 30  # 30 seconds between resends

# ========================= SECURITY SETTINGS =========================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Password validation settings
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

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# ========================= MESSAGE TAGS =========================

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
    
}

# ========================= DEFAULT SETTINGS =========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========================= LOGGING CONFIGURATION =========================
# For debugging OTP issues

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'beststore.log',
            'formatter': 'verbose',
        },
        'email_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'email.log',
            'formatter': 'verbose',
        },
        'otp_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'otp.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['console', 'file', 'otp_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.core.mail': {
            'handlers': ['console', 'email_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
import os
LOGS_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# ========================= HEROKU DEPLOYMENT =========================

# Activate Django-Heroku settings (for Heroku deployment)
# django_heroku.settings(locals())  # Comment out for local development

# For Heroku, uncomment above and add these:
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True