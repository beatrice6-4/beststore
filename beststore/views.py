from django.shortcuts import render
from store.models import Product
from django.contrib.auth.decorators import login_required

def home(request):
    products = Product.objects.all().filter(is_available=True)  # Fetch all available products rom the database


    context = {'products': products}

    return render(request, 'home.html', context)






from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.utils.translation import activate
from django.views.i18n import set_language as django_set_language
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

# ============ HOME PAGE ============
def home(request):
    """
    Display the home page with featured products and categories.
    """
    from store.models import Product
    from category.models import Category
    
    context = {
        'page_title': 'Home | Mama Maasai Bakers',
        'featured_products': Product.objects.filter(is_available=True)[:8],
        'categories': Category.objects.all()[:6],
    }
    
    return render(request, 'index.html', context)


# ============ LANGUAGE SELECTION ============
@require_http_methods(["POST"])
def set_language(request, language=None):
    """
    Set the user's language preference.
    Supports both POST and GET requests.
    """
    if language:
        # If language is passed in URL
        activate(language)
        if request.user.is_authenticated:
            request.user.preferred_language = language
            request.user.save()
        
        response = redirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response
    
    # Handle POST request from Django's i18n form
    response = django_set_language(request)
    
    # Log language change
    logger.info(f"Language changed by {request.user if request.user.is_authenticated else 'Anonymous'}")
    
    return response


# ============ CUSTOM ERROR PAGES ============
def handler400(request, exception=None):
    """
    Handle 400 - Bad Request errors.
    """
    context = {
        'error_code': 400,
        'error_title': 'Bad Request',
        'error_message': 'The request could not be understood by the server.',
    }
    return render(request, 'errors/error.html', context, status=400)


def handler403(request, exception=None):
    """
    Handle 403 - Forbidden errors.
    """
    context = {
        'error_code': 403,
        'error_title': 'Forbidden',
        'error_message': 'You do not have permission to access this resource.',
    }
    return render(request, 'errors/error.html', context, status=403)


def handler404(request, exception=None):
    """
    Handle 404 - Page Not Found errors.
    """
    context = {
        'error_code': 404,
        'error_title': 'Page Not Found',
        'error_message': 'The page you are looking for could not be found.',
    }
    return render(request, 'errors/error.html', context, status=404)


def handler500(request):
    """
    Handle 500 - Server Error.
    """
    context = {
        'error_code': 500,
        'error_title': 'Server Error',
        'error_message': 'An unexpected error occurred on our server.',
    }
    logger.error("500 Server Error", exc_info=True)
    return render(request, 'errors/error.html', context, status=500)


# ============ UTILITY VIEWS ============
def get_csrf_token(request):
    """
    Return CSRF token for AJAX requests.
    """
    from django.middleware.csrf import get_token
    
    token = get_token(request)
    return JsonResponse({'csrfToken': token})


@login_required(login_url='login')
def dashboard(request):
    """
    User dashboard view.
    """
    context = {
        'page_title': 'Dashboard',
        'user': request.user,
    }
    return render(request, 'accounts/dashboard.html', context)


def about(request):
    """
    About page view.
    """
    context = {
        'page_title': 'About Us | Mama Maasai Bakers',
    }
    return render(request, 'about.html', context)


def privacy_policy(request):
    """
    Privacy policy page view.
    """
    context = {
        'page_title': 'Privacy Policy | Mama Maasai Bakers',
    }
    return render(request, 'legal/privacy_policy.html', context)


def terms_of_service(request):
    """
    Terms of service page view.
    """
    context = {
        'page_title': 'Terms of Service | Mama Maasai Bakers',
    }
    return render(request, 'legal/terms_of_service.html', context)


def sitemap(request):
    """
    Sitemap view for SEO.
    """
    from store.models import Product
    from category.models import Category
    
    context = {
        'products': Product.objects.filter(is_available=True),
        'categories': Category.objects.all(),
    }
    return render(request, 'sitemap.xml', context, content_type='application/xml')