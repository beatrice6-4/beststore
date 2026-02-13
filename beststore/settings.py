import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-kds8lcf_2yb3w_!l!qn=k(tc6^y_%4*nbsw5h62)_t8%4((a-4')
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'mamamaasaibakers.onrender.com', 'mamamaasaibakers.com', 'dianah-dad5dcff9a01.herokuapp.com', '*.herokuapp.com']

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
    'school',
    'loans',
    'lms',
    'cloudinary_storage',
    'cloudinary',
]

JAZZMIN_SETTINGS = {
    "site_title": "BestStore Admin",
    "site_header": "BestStore",
    "site_brand": "BestStore",
    "welcome_sign": "Welcome to BestStore administration",
    "copyright": "BestStore © 2025",
    "search_model": "store.Product",
    "user_avatar": "img/user-avatar.png",
    "show_sidebar": True,
    "navigation_expanded": False,
    "related_modal_active": True,
    "custom_css": "css/jazzmin-custom.css",
    "custom_js": "js/jazzmin-custom.js",
    "topmenu_links": [
        {"name": "Home", "url": "/", "new_window": False},
        {"name": "Docs", "url": "/docs/", "new_window": True},
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "store": "fas fa-store",
        "orders": "fas fa-shopping-cart",
        "carts": "fas fa-shopping-cart",
        "category": "fas fa-tags",
        "accounts": "fas fa-user",
        "finance": "fas fa-dollar-sign",
        "CDMIS": "fas fa-book-medical",
        "school": "fas fa-school",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "bg-success",
    "accent": "accent-success",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar_scrollbar_small": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
}

AUTHENTICATION_BACKENDS = [
    'backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
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

# Database configuration - Use PostgreSQL on Heroku, SQLite locally
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dhklmtpxy',
    'API_KEY': '345437392578237',
    'API_SECRET': 'Vz5iaCXqJlNOO3oCQ-41J-tsVbA',
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'mamamaassaibakers@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'ujqc yeoo sagb zajx')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'mamamaassaibakers@gmail.com')

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Settings for Development (HTTP)
# Disable HTTPS redirects and secure cookies for local development
if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_BROWSER_XSS_FILTER = False
    SECURE_CONTENT_SECURITY_POLICY = None
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
else:
    # Production settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True