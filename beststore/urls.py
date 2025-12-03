"""
Mama Maasai Bakers - URL Configuration
"""
from django.contrib import admin
from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    # Apps
    path('accounts/', include('accounts.urls')),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('orders/', include('orders.urls')),
    path('cdmis/', include('CDMIS.urls')),
    path('cart/', include('carts.urls')),  # Carts app URLs
    
    # API endpoints
    path('api/', include('api.urls')) if 'api' in settings.INSTALLED_APPS else None,
]

# Remove None entries
urlpatterns = [url for url in urlpatterns if url is not None]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
