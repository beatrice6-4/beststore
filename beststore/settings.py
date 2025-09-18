
import os
from pathlib import Path
import django_heroku
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-^+e$ae-he)jy#6e0d(h*+0-c=*j9%)v_a$z6y#-6qxsxuq&ydb'

DEBUG = True

ALLOWED_HOSTS = ['*']

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
]



JET_REBOOT_SETTINGS = {
    'site_title': 'BestStore Admin',
    'site_logo': '/static/images/logo.png',
    'welcome_sign': 'Welcome to BestStore Admin',
    'copyright': '© 2023 BestStore. All rights reserved.',
    'search_model': 'auth.User',
    'show_recent_actions': True,
    'language_chooser': True,
    'custom_css': '/static/css/custom.css',
    'custom_js': '/static/js/custom.js',

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



MPESA_CONSUMER_KEY = 'QoZMbK2rzLOisAZsAZkS5GM1MEu3mSevGXv9N9z7oyzaaTUS'
MPESA_CONSUMER_SECRET = '75PYlNNbxGfj0nZUGGzdLAuxJaSl2fWIlQ0yOA9wlN7SyMkxc34QAOfrmMl40Q3Z'
MPESA_SHORTCODE = '20306'
MPESA_PASSKEY = '20306bfb279f9aa9b7b5c3f1c2e8d8f9e0d97f0f6c6e3d3e5b4a3f4e5d6c7b8a9'
MPESA_BASE_URL = 'https://sandbox.safaricom.co.ke'  # Use production URL for live

MPESA_CALLBACK_URL = 'https://mamamaassaibakers.herokuapp.com/orders/payments/'



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


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mamamaassaibakers@gmail.com'
EMAIL_HOST_PASSWORD = 'ujqc yeoo sagb zajx'
DEFAULT_FROM_EMAIL = 'mamamaassaibakers@gmail.com'

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
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
import os
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (user-uploaded content, e.g., product images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

django_heroku.settings(locals())
