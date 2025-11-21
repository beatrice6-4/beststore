from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import logging
import uuid

from .forms import (
    RegistrationForm, UserForm, ContactForm,
    WishlistForm, UserProfileForm, PasswordChangeForm,
    DerivConnectionForm, SearchForm, CategoryForm
)
from .models import (
    Account, ContactMessage, Wishlist,
    UserProfile, Category
)

logger = logging.getLogger(__name__)


# ============ HELPER FUNCTIONS ============
def is_valid_uuid(uuid_string):
    """Check if string is valid UUID"""
    try:
        uuid.UUID(str(uuid_string))
        return True
    except (ValueError, AttributeError):
        return False


# ============ AUTHENTICATION VIEWS ============
def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please login.')
            logger.info(f'New user registered: {user.email}')
            return redirect('accounts/login.html')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Register',
    }
    return render(request, 'accounts/register.html', context)


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, 'accounts/login.html', {'page_title': 'Login'})
        
        try:
            user = Account.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                logger.info(f'User logged in: {user.email}')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
                logger.warning(f'Failed login attempt for: {email}')
        except Account.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            logger.warning(f'Login attempt with non-existent email: {email}')
    
    context = {'page_title': 'Login'}
    return render(request, 'accounts/login.html', context)


@login_required(login_url='accounts:login')
def logout_view(request):
    """User logout view"""
    email = request.user.email
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    logger.info(f'User logged out: {email}')
    return redirect('accounts:login')




def forgot_password(request):
    """Handle forgot password request"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Account.objects.get(email=email)
            # Send password reset email here
            messages.success(request, 'Password reset link has been sent to your email.')
        except Account.DoesNotExist:
            messages.error(request, 'Email address not found.')
        return redirect('login')
    return render(request, 'accounts/forgot_password.html')


# ============ PROFILE VIEWS ============
@login_required(login_url='accounts:login')
def dashboard(request):
    """User dashboard view"""
    user = request.user
    profile = user.trading_profile
    
   
    

    
    context = {
        'page_title': 'Dashboard',
        'profile': profile,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='accounts:login')
def profile(request):
    """User profile view"""
    user = request.user
    profile = user.trading_profile
    

    


@login_required(login_url='accounts:login')
def edit_profile(request):
    """Edit user profile view"""
    user = request.user
    profile = user.trading_profile
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            logger.info(f'Profile updated for: {user.email}')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Error updating profile. Please check the form.')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'page_title': 'Edit Profile',
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='accounts:login')
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully! Please login again.')
                logger.info(f'Password changed for: {user.email}')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Old password is incorrect.')
    else:
        form = PasswordChangeForm()
    
    context = {
        'page_title': 'Change Password',
        'form': form,
    }
    return render(request, 'accounts/change_password.html', context)



# ============ CONTACT VIEW ============
def contact(request):
    """Contact form view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            messages.success(request, 'Message sent successfully! We will get back to you soon.')
            logger.info(f'Contact message received from {contact_msg.email}')
            return redirect('home')
        else:
            messages.error(request, 'Error sending message.')
    else:
        form = ContactForm()
    
    context = {
        'page_title': 'Contact Us',
        'form': form,
    }
    return render(request, 'accounts/contact.html', context)


# ============ WISHLIST VIEWS ============
@login_required(login_url='accounts:login')
def wishlist(request):
    """User wishlist view"""
    user = request.user
    wishlist_items = Wishlist.objects.filter(user=user).order_by('-added_at')
    
    context = {
        'page_title': 'My Wishlist',
        'wishlist_items': wishlist_items,
    }
    return render(request, 'accounts/wishlist.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
@csrf_exempt
def add_to_wishlist(request):
    """Add item to wishlist via AJAX"""
    try:
        product_id = request.POST.get('product_id', '').strip()
        product_name = request.POST.get('product_name', '').strip()
        
        if not product_id or not product_name:
            return JsonResponse({
                'success': False,
                'error': 'Missing product information'
            }, status=400)
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product_id=product_id,
            defaults={'product_name': product_name}
        )
        
        if created:
            logger.info(f'Product added to wishlist by {request.user.email}')
            return JsonResponse({
                'success': True,
                'message': 'Added to wishlist!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Item already in wishlist'
            })
    except Exception as e:
        logger.error(f'Error adding to wishlist: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': 'Error adding to wishlist'
        }, status=500)


@login_required(login_url='accounts:login')
def remove_from_wishlist(request, item_id):
    """Remove item from wishlist"""
    if not is_valid_uuid(item_id):
        messages.error(request, 'Invalid item ID.')
        return redirect('accounts:wishlist')
    
    try:
        wishlist_item = Wishlist.objects.get(id=item_id, user=request.user)
        wishlist_item.delete()
        messages.success(request, 'Removed from wishlist')
        logger.info(f'Item removed from wishlist by {request.user.email}')
        return redirect('accounts:wishlist')
    except (Wishlist.DoesNotExist, ValueError):
        messages.error(request, 'Item not found.')
        return redirect('accounts:wishlist')


# ============ CATEGORY VIEWS ============
def categories(request):
    """List all categories"""
    categories_list = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_title': 'Categories',
        'categories': categories_list,
    }
    return render(request, 'accounts/categories.html', context)


def category_detail(request, slug):
    """Category detail view"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    context = {
        'page_title': category.name,
        'category': category,
    }
    return render(request, 'accounts/category_detail.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(["GET", "POST"])
def manage_categories(request):
    """Manage categories (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            logger.info(f'Category created by {request.user.email}')
            return redirect('accounts:manage_categories')
    else:
        form = CategoryForm()
    
    categories_list = Category.objects.all().order_by('-created_at')
    
    context = {
        'page_title': 'Manage Categories',
        'form': form,
        'categories': categories_list,
    }
    return render(request, 'accounts/manage_categories.html', context)


# ============ SEARCH VIEW ============
def search(request):
    """Search view"""
    form = SearchForm(request.GET or None)
    results = []
    query = ''
    
    if request.GET.get('q'):
        query = request.GET.get('q', '').strip()
        results = Category.objects.filter(
            name__icontains=query,
            is_active=True
        )
    
    context = {
        'page_title': 'Search Results',
        'form': form,
        'results': results,
        'query': query,
    }
    return render(request, 'accounts/search.html', context)


# ============ ERROR VIEWS ============
def custom_404(request, exception=None):
    """Custom 404 error page"""
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    """Custom 500 error page"""
    return render(request, 'errors/500.html', status=500)


def custom_403(request, exception=None):
    """Custom 403 error page"""
    return render(request, 'errors/403.html', status=403)


def custom_400(request, exception=None):
    """Custom 400 error page"""
    return render(request, 'errors/400.html', status=400)