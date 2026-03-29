"""
WSGI config for BestStore project - Apache Deployment Optimized

This configuration is specifically tuned for production deployment
with Apache and mod_wsgi.

For more information on this file, see:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
DJANGO_PROJECT_PATH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DJANGO_PROJECT_PATH))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beststore.settings')

# Configure Django settings
django.setup()

# Import after Django setup
from django.core.wsgi import get_wsgi_application

# Get the WSGI application
application = get_wsgi_application()

# Optional: Wrap with middleware for better error reporting
try:
    from django.middleware.wsgi import WSGIRequest
    
    # Log WSGI import information (useful for debugging)
    print(f"Django WSGI Application Loaded Successfully")
    print(f"Django Project Path: {DJANGO_PROJECT_PATH}")
    print(f"Django Settings Module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    
except Exception as e:
    print(f"Error loading WSGI application: {e}")
    raise

# Export application for Apache mod_wsgi
__version__ = '1.0'
