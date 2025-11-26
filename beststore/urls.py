"""
Mama Maasai Bakers - URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from orders.views import mpesa_transaction_result
from . import views

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    path('school/', include('school.urls')),
    
    # Home
    path('', views.home, name='home'),
    
    # Apps
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('cdmis/', include('CDMIS.urls')),

    path('mpesa/transaction/result/', mpesa_transaction_result, name='mpesa_transaction_result'),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)