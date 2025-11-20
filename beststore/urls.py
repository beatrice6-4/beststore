"""
URL configuration for beststore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
    
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from . import views

# ============ ADMIN CUSTOMIZATION ============
admin.site.site_header = "Mama Maasai Bakers Admin"
admin.site.site_title = "Admin | Mama Maasai Bakers"
admin.site.index_title = "Welcome to Mama Maasai Bakers Admin"

# ============ MAIN URL PATTERNS ============
urlpatterns = [
    # ============ INTERNATIONALIZATION ============
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/<str:language>/', views.set_language, name='set_language'),
    
    # ============ ADMIN PANEL ============
    path('admin/', admin.site.urls),
    
    # ============ AUTHENTICATION ============
    path('accounts/', include('accounts.urls')),
    
    # ============ MAIN PAGES ============
    path('', views.home, name='home'),
    path('contact/', include('accounts.urls', namespace='contact')),
    
    # ============ STORE & PRODUCTS ============
    path('store/', include('store.urls')),
    path('category/', include('category.urls')),
    
    # ============ SHOPPING CART & ORDERS ============
    path('cart/', include('carts.urls')),
    path('orders/', include('orders.urls')),
    
    # ============ CDMIS - COMMUNITY DEVELOPMENT ============
    path('cdmis/', include('CDMIS.urls')),
    
    # ============ FINANCE ============
    path('finance/', include('finance.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ============ STATIC FILES IN DEBUG MODE ============
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # ============ DEBUG TOOLBAR (OPTIONAL) ============
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]

# ============ CUSTOM ERROR HANDLERS ============
handler404 = 'beststore.views.handler404'
handler500 = 'beststore.views.handler500'
handler403 = 'beststore.views.handler403'
handler400 = 'beststore.views.handler400'