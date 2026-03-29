# Django Settings Configuration for Apache Deployment

This document outlines the recommended settings.py configuration for 
production deployment with Apache and mod_wsgi.

## Key Settings for Apache Production

### 1. Debug Mode
```python
# PRODUCTION - Must be False
DEBUG = False

# DEVELOPMENT - Can be True
# DEBUG = True
```

### 2. Allowed Hosts
```python
# Only include your domain and www subdomain
ALLOWED_HOSTS = [
    'mamamaasaibakers.com',
    'www.mamamaasaibakers.com',
    'localhost',  # For local testing
    '127.0.0.1',  # For local testing
]
```

### 3. Secret Key
```python
# Use environment variable, NOT hardcoded
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'change-me-in-production-use-env-variable'
)

# To generate a new secret key:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 4. Database Configuration for Apache
```python
import dj_database_url

# Use PostgreSQL for production (recommended for Apache)
if os.environ.get('DATABASE_URL'):
    # Production: Use environment variable
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,  # Connection pooling (10 minutes)
            atomic_requests=False,  # Let database handle transactions
        )
    }
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'beststore_db',
            'USER': 'beststore_user',
            'PASSWORD': 'password_here',
            'HOST': 'localhost',
            'PORT': '5432',
            'ATOMIC_REQUESTS': False,
            'CONN_MAX_AGE': 600,
        }
    }
```

### 5. Static Files Configuration
```python
# Static files for Apache deployment
STATIC_URL = '/static/'

# Where Django collects static files for Apache to serve
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional directories to collect from
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Use WhiteNoise for better static file handling
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 6. Media Files Configuration
```python
# Media files uploaded by users
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Use Cloudinary for media storage (as configured)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Alternatively, use local filesystem:
# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}
```

### 7. Security Settings for Production
```python
# SSL/TLS Configuration
SECURE_SSL_REDIRECT = True  # Force HTTPS
SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
CSRF_COOKIE_SECURE = True  # CSRF tokens only over HTTPS

# HTTP Strict Transport Security
SECURE_HSTS_SECONDS = 31536000  # 1 year (recommended for production)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Include subdomains
SECURE_HSTS_PRELOAD = True  # Allow browser preload list

# Content Security Policy
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "cdn.jsdelivr.net"),
    "style-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net"),
    "img-src": ("'self'", "data:", "https:"),
    "font-src": ("'self'", "cdn.jsdelivr.net"),
}

# Additional Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"

# Cookie settings
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400 * 7  # 7 days

# Other security settings
ALLOWED_HOSTS_WITH_SSL = True
CSRF_COOKIE_DOMAIN = 'mamamaasaibakers.com'
SESSION_COOKIE_DOMAIN = 'mamamaasaibakers.com'
```

**Development Override** (for testing without HTTPS):
```python
if DEBUG:
    # Disable security features for local development
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
```

### 8. WSGI Configuration
```python
# Production WSGI application
WSGI_APPLICATION = 'beststore.wsgi.application'
```

### 9. Middleware for Apache
```python
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be first after SecurityMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 10. Logging Configuration for Apache
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
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
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(exist_ok=True)
```

### 11. Template Configuration
```python
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
                'django.template.context_processors.media',  # For media files
                'django.template.context_processors.static',  # For static files
                'category.context_processors.menu_links',
                'carts.context_processors.counter',
            ],
            'debug': DEBUG,  # Template debugging in development only
        },
    },
]
```

### 12. Session Configuration
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Database sessions
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # Only over HTTPS
SESSION_SAVE_EVERY_REQUEST = True  # Save session on every request (adjust as needed)
```

### 13. Cache Configuration (Optional but Recommended)
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'beststore_cache',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
```

For Redis cache (if you have Redis):
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50}
        }
    }
}
```

## Environment Variables (.env file)

Create a `.env` file in `/var/www/mamamaasaibakers/`:

```
# Django Settings
DEBUG=False
DJANGO_SECRET_KEY=your-very-long-random-secret-key-here
ALLOWED_HOSTS=mamamaasaibakers.com,www.mamamaasaibakers.com

# Database
DATABASE_URL=postgresql://beststore_user:password@localhost:5432/beststore_db

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Cloudinary (for media storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# AWS S3 (if using S3 instead of Cloudinary)
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1
AWS_S3_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

## Pre-Deployment Checklist

- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` uses environment variable
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] `SECURE_SSL_REDIRECT = True` for HTTPS
- [ ] Database properly configured and tested
- [ ] `STATIC_ROOT` and `STATICFILES_DIRS` configured
- [ ] `MEDIA_ROOT` and `MEDIA_URL` configured
- [ ] Email configuration working
- [ ] All environment variables in `.env` file
- [ ] Logging directory exists and is writable
- [ ] `.env` file has proper permissions (600)
- [ ] Tests pass: `python manage.py test`
- [ ] System check passes: `python manage.py check`
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] Database migrated: `python manage.py migrate`

## Security Validation

```bash
# Check for security issues
python manage.py check --deploy

# This will report any Django security configuration issues
```

The output should show no errors or warnings about security settings.

## Performance Tuning

### Reduce Database Connections
```python
DATABASES['default']['CONN_MAX_AGE'] = 600  # Reuse connections for 10 minutes
```

### Enable QuerySet Optimization
```python
# Use select_related() for foreign keys
User.objects.select_related('profile')

# Use prefetch_related() for reverse foreign keys
Post.objects.prefetch_related('comments')
```

### Cache Template Rendering
```python
# Use {% cache %} template tag
# Implement view-level caching
# Use Django's cache framework
```

---

**Last Updated**: 2026-03-21
**Django Version**: 5.2+
**Python Version**: 3.8+
