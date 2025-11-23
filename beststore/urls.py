"""
Mama Maasai Bakers - URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Home
    path('', views.dashboard, name='dashboard'),
    
    # Apps
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('category/', include('category.urls')),
    path('cdmis/', include('CDMIS.urls')),
    path('finance/', include('finance.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)