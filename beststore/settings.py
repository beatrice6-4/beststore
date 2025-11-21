import os
from pathlib import Path
import django_heroku
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-kds8lcf_2yb3w_!l!qn=k(tc6^y_%4*nbsw5h62)_t8%4((a-4')

DEBUG = os.environ.get('DEBUG', 'False') == 'False'

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
    'cloudinary',
    'cloudinary_storage',
]

# ============ JAZZMIN ADMIN CONFIGURATION ============
JAZZMIN_SETTINGS = {
    # ========== BRANDING ==========
    "site_title": "Mama Maasai Bakers",
    "site_header": "Mama Maasai Bakers Admin",
    "site_brand": "Mama Maasai Bakers",
    "brand_html": """
        <img src="/static/images/gov.png" alt="Logo" style="width: 40px; height: 40px; margin-right: 10px; border-radius: 50%;">
        <strong>Mama Maasai Bakers</strong>
    """,
    "welcome_sign": "Welcome to Admin Dashboard",
    "copyright": "Mama Maasai Bakers © 2025. All rights reserved.",
    
    # ========== SIDEBAR & NAVIGATION ==========
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
    
    # ========== SEARCH CONFIGURATION ==========
    "search_model": [
        "accounts.Account",
        "store.Product",
        "category.Category",
        "orders.Order",
        "CDMIS.Group",
        "finance.Payment",
    ],
    
    # ========== CUSTOM LINKS ==========
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
                "url": "https://mamamaasaibakers.com/cdmis/finance/",
                "icon": "fas fa-money-bill-wave",
                "new_window": True,
                "permissions": ["finance.view_financerecord"]
            },
        ]
    },
    
    # ========== ICONS FOR MODELS ==========
    "icons": {
        # Accounts
        "accounts.Account": "fas fa-user-circle",
        "accounts.ContactMessage": "fas fa-envelope",
        "accounts.Transaction": "fas fa-exchange-alt",
        
        # Store
        "store.Product": "fas fa-box",
        "store.ProductGallery": "fas fa-images",
        "store.Variation": "fas fa-sliders-h",
        
        # Category
        "category.Category": "fas fa-list",
        
        # Cart & Orders
        "carts.Cart": "fas fa-shopping-cart",
        "carts.CartItem": "fas fa-shopping-bag",
        "orders.Order": "fas fa-receipt",
        "orders.OrderProduct": "fas fa-package",
        "orders.Payment": "fas fa-credit-card",
        
        # CDMIS
        "CDMIS.Group": "fas fa-people-carry",
        "CDMIS.Payment": "fas fa-money-bill",
        "CDMIS.Training": "fas fa-graduation-cap",
        "CDMIS.Requirement": "fas fa-tasks",
        
        # Finance
        "finance.FinanceRecord": "fas fa-chart-bar",
    },
    
    # ========== DEFAULT ICONS ==========
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # ========== UI CONFIGURATION ==========
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
    
    # ========== FORM CONFIGURATION ==========
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        # Accounts
        "accounts.Account": "single",
        "accounts.ContactMessage": "single",
        "accounts.Transaction": "single",
        
        # Store
        "store.Product": "collapsible",
        "store.ProductGallery": "single",
        "store.Variation": "single",
        
        # Category
        "category.Category": "single",
        
        # Orders
        "orders.Order": "horizontal_tabs",
        "orders.OrderProduct": "single",
        "orders.Payment": "single",
        
        # CDMIS
        "CDMIS.Group": "collapsible",
        "CDMIS.Payment": "single",
        "CDMIS.Training": "single",
        "CDMIS.Requirement": "single",
        
        # Finance
        "finance.FinanceRecord": "horizontal_tabs",
    },
    
    # ========== MODAL CONFIGURATION ==========
    "related_modal_active": True,
    "list_filter_toggle": True,
    "list_per_page": 25,
    
    # ========== THEME COLORS ==========
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

# ============ JAZZMIN UI TWEAKS ============
JAZZMIN_UI_TWEAKS = {
    "navbar_small": False,
    "footer_small": False,
    "body_small": False,
    "brand_small": False,
    "brand_colour": "navbar-navy",
    "accent": "accent-primary",
    "toolbar_fixed": True,
    "sidebar_fixed": True,
    "sidebar_navigation_collapse": False,
    "theme": "default",
    "dark_mode_theme": "darkly",
}

# ============ SESSION CONFIGURATION ============
SESSION_COOKIE_AGE = 2400  # 40 minutes in seconds
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = True  # For HTTPS
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True  # For HTTPS

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
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://beststore_django_render_user:jg79k7m3AvDtfKKfXcdHOwQa9QyLEF6F@dpg-d3sckm3e5dus73e162vg-a.oregon-postgres.render.com/beststore_django_render',
        conn_max_age=600
    )
}

# ============ CLOUDINARY STORAGE ============
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'df44dwnwg',
    'API_KEY': '626193889524544',
    'API_SECRET': 'r40hH_tPzZ8BRQKaTKnb-2ZdAfU',
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# ============ EMAIL CONFIGURATION ============
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
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
}

# ============ DEFAULT FIELD TYPE ============
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============ SECURITY SETTINGS ============
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net"),
    "style-src": ("'self'", "'unsafe-inline'", "fonts.googleapis.com", "cdn.jsdelivr.net"),
    "font-src": ("'self'", "fonts.gstatic.com"),
    "img-src": ("'self'", "data:", "https:"),
}
X_FRAME_OPTIONS = "SAMEORIGIN"

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
            'filename': BASE_DIR / 'logs' / 'debug.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
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
    },
}

# ============ CACHE CONFIGURATION ============
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mama-maasai-cache',
    }
}



# ============ DERIV TRADING CONFIGURATION ============
DERIV_APP_ID = os.environ.get('DERIV_APP_ID', 'YOUR_DERIV_APP_ID')
DERIV_API_TOKEN = os.environ.get('DERIV_API_TOKEN', '')
DERIV_API_URL = 'https://api.deriv.com/api'

# ============ ACTIVATE DJANGO-HEROKU SETTINGS ============
django_heroku.settings(locals())