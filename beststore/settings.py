import os
from pathlib import Path
import dj_database_url
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent

# ============ CREATE NECESSARY DIRECTORIES ============
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

MEDIA_ROOT_DIR = BASE_DIR / 'mediafiles'
MEDIA_ROOT_DIR.mkdir(exist_ok=True)

# ============ SECURITY SETTINGS ============
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-kds8lcf_2yb3w_!l!qn=k(tc6^y_%4*nbsw5h62)_t8%4((a-4')
DEBUG = os.environ.get('DEBUG', 'False') == 'False'
ALLOWED_HOSTS = ['*'] if DEBUG else os.environ.get('ALLOWED_HOSTS', 'mamamaasaibakers.com').split(',')  # FIXED: Allow all in DEBUG

# ============ INSTALLED APPS ============
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

]

# ============ JAZZMIN ADMIN CONFIGURATION ============
JAZZMIN_SETTINGS = {
    "site_title": "Mama Maasai Bakers",
    "site_header": "Mama Maasai Bakers Admin",
    "site_brand": "Mama Maasai Bakers",
    "brand_html": """
        <img src="/static/images/gov.png" alt="Logo" style="width: 40px; height: 40px; margin-right: 10px; border-radius: 50%;">
        <strong>Mama Maasai Bakers</strong>
    """,
    "welcome_sign": "Welcome to Admin Dashboard",
    "copyright": "Mama Maasai Bakers © 2025. All rights reserved.",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "accounts",
        "store",
        "category",
        "orders",
        "carts",
        "CDMIS",
        "finance",
    ],
    "search_model": [
        "accounts.Account",
        "store.Product",
        "category.Category",
        "orders.Order",
        "CDMIS.Group",
        "finance.FinanceRecord",
    ],
    "custom_links": {
        "accounts": [
            {
                "name": "🌐 View Website",
                "url": "https://mamamaasaibakers.com",
                "icon": "fas fa-globe",
                "new_window": True,
                "permissions": ["accounts.view_account"]
            },
            {
                "name": "📊 CDMIS Portal",
                "url": "https://mamamaasaibakers.com/cdmis/groups",
                "icon": "fas fa-chart-line",
                "new_window": True,
                "permissions": ["CDMIS.view_group"]
            },
            {
                "name": "💰 Finance Dashboard",
                "url": "https://mamamaasaibakers.com/finance/",
                "icon": "fas fa-money-bill-wave",
                "new_window": True,
                "permissions": ["finance.view_financerecord"]
            },
        ]
    },
    "icons": {
        "accounts.Account": "fas fa-user-circle",
        "accounts.ContactMessage": "fas fa-envelope",
        "accounts.Transaction": "fas fa-exchange-alt",
        "accounts.TradeHistory": "fas fa-chart-line",
        "accounts.UserProfile": "fas fa-user-cog",
        "accounts.Wishlist": "fas fa-heart",
        "accounts.Category": "fas fa-tag",
        "store.Product": "fas fa-box",
        "store.ProductGallery": "fas fa-images",
        "store.Variation": "fas fa-sliders-h",
        "category.Category": "fas fa-list",
        "carts.Cart": "fas fa-shopping-cart",
        "carts.CartItem": "fas fa-shopping-bag",
        "orders.Order": "fas fa-receipt",
        "orders.OrderProduct": "fas fa-package",
        "orders.Payment": "fas fa-credit-card",
        "CDMIS.Group": "fas fa-people-carry",
        "CDMIS.Payment": "fas fa-money-bill",
        "CDMIS.Training": "fas fa-graduation-cap",
        "CDMIS.Requirement": "fas fa-tasks",
        "finance.FinanceRecord": "fas fa-chart-bar",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "show_ui_builder": False,
    "ui_tweaks": {
        "navbar_small": False,
        "footer_small": False,
        "body_small": False,
        "brand_small": False,
        "brand_colour": "navbar-primary",
        "accent": "accent-primary",
        "toolbar_fixed": True,
        "sidebar_fixed": True,
        "sidebar_navigation_collapse": False,
    },
    "changeform_format": "horizontal_tabs",
    "related_modal_active": True,
    "list_filter_toggle": True,
    "list_per_page": 25,
    "theme": {
        "primary-color": "#1f3a5f",
        "primary-dark": "#1a2f47",
        "secondary-color": "#2980b9",
        "success-color": "#27ae60",
        "warning-color": "#f39c12",
        "danger-color": "#e74c3c",
        "info-color": "#3498db",
    },
}


# ============ SESSION CONFIGURATION ============
SESSION_COOKIE_AGE = 2400
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# ============ MIDDLEWARE ============
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

# ============ URL CONFIGURATION ============
ROOT_URLCONF = 'beststore.urls'
LOGIN_REDIRECT_URL = 'redirect_after_login'
LOGIN_URL = 'login'

# ============ TEMPLATES ============
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

# ============ USER MODEL ============
AUTH_USER_MODEL = 'accounts.Account'

# ============ DATABASE CONFIGURATION ============
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============ CLOUDINARY STORAGE ============
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'df44dwnwg'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '626193889524544'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'r40hH_tPzZ8BRQKaTKnb-2ZdAfU'),
}

if not DEBUG:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# ============ EMAIL CONFIGURATION ============
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'mamamaassaibakers@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'ujqc yeoo sagb zajx')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'mamamaassaibakers@gmail.com')

# ============ PASSWORD VALIDATION ============
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

# ============ INTERNATIONALIZATION ============
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# ============ STATIC FILES ============
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ============ MESSAGE TAGS ============
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.INFO: 'info',
}

# ============ DEFAULT FIELD TYPE ============
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============ SECURITY SETTINGS ============
SECURE_SSL_REDIRECT = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"),
    "style-src": ("'self'", "'unsafe-inline'", "fonts.googleapis.com", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"),
    "font-src": ("'self'", "fonts.gstatic.com", "cdnjs.cloudflare.com"),
    "img-src": ("'self'", "data:", "https:", "res.cloudinary.com"),
    "media-src": ("'self'", "https:", "res.cloudinary.com"),
    "connect-src": ("'self'", "https:", "res.cloudinary.com", "api.deriv.com"),
}
X_FRAME_OPTIONS = "SAMEORIGIN"

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ============ LOGGING CONFIGURATION ============
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
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
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'debug.log'),  # Convert to string for compatibility
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'store': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'orders': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'carts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============ CACHE CONFIGURATION ============
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mama-maasai-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# ============ DERIV TRADING CONFIGURATION ============
DERIV_APP_ID = os.environ.get('DERIV_APP_ID', 'YOUR_DERIV_APP_ID')
DERIV_API_TOKEN = os.environ.get('DERIV_API_TOKEN', '')
DERIV_API_URL = 'https://api.deriv.com/api'
DERIV_WS_URL = 'wss://ws.binaryx.com/websockets/v3'

# ============ PAGINATION ============
ITEMS_PER_PAGE = 12
TRADES_PER_PAGE = 10
TRANSACTIONS_PER_PAGE = 10

# ============ FILE UPLOAD SETTINGS ============
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
ALLOWED_UPLOAD_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx']

# ============ CSRF TRUSTED ORIGINS ============
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')

# ============ TESTING ============
if 'test' in os.sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }