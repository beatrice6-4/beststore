from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, LoginForm
from .models import Account
from orders.models import Order, OrderProduct
from .forms import RegistrationForm, UserForm, LoginForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart, CartItem


def register(request):
    """User registration with email verification."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION EMAIL
            current_site = get_current_site(request)
            mail_subject = 'Verify Your Email - BESTSTORE'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(
                mail_subject, 
                message, 
                'noreply@beststore.com',
                [to_email]
            )
            send_email.content_subtype = 'html'
            send_email.send()
            
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    
    context = {'form': form}
    return render(request, 'accounts/register.html', context)

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def login(request):
    """
    Authenticate user and redirect strictly by role:
      - finance -> finance_dashboard
      - admin (is_staff/is_superuser or role=='admin') -> admin_dashboard
      - others -> dashboard
    Also attempts to merge anonymous cart items into the user's cart if cart models exist.
    """
    from django.contrib import auth, messages
    from django.shortcuts import render, redirect

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['email']  # Can be email or username
            password = form.cleaned_data['password']

            # try authenticate by email first, then username
            user = auth.authenticate(request, email=identifier, password=password)
            if user is None:
                user = auth.authenticate(request, username=identifier, password=password)

            if user is not None:
                # merge anonymous cart into user cart if cart models/helpers exist
                try:
                    from carts.models import Cart, CartItem
                    from carts.views import _cart_id
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    cart_items = CartItem.objects.filter(cart=cart)
                    for item in cart_items:
                        item.user = user
                        item.save()
                except Exception:
                    # ignore if cart app/names differ or any error during merge
                    pass

                auth.login(request, user)
                messages.success(request, 'You are now logged in the system.')

                role = getattr(user, 'role', None)
                # Strict role-based redirect
                if role == 'finance':
                    return redirect('finance_dashboard')
                if user.is_staff or user.is_superuser or role == 'admin':
                    return redirect('admin_dashboard')
                return redirect('dashboard')

            messages.error(request, 'Invalid login credentials, try again')
            return redirect('login')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out of the system.')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link, register again')
        return redirect('register')


from store.models import Product  # Import the Product model

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

@login_required
def dashboard(request):
    """
    Display user dashboard with orders, spending, and featured products.
    Shows personalized statistics and quick access to frequently used features.
    """
    from store.models import Product, Order, OrderItem
    
    user = request.user
    
    # ========================= ORDERS STATISTICS =========================
    # Get all orders for current user
    all_orders = Order.objects.filter(user=user).select_related('user')
    
    # Calculate total orders
    total_orders = all_orders.count()
    
    # Calculate completed orders
    completed_orders = all_orders.filter(
        status__in=['completed', 'delivered', 'confirmed']
    ).count()
    
    # Calculate pending orders
    pending_orders = all_orders.filter(
        status__in=['pending', 'processing', 'shipped']
    ).count()
    
    # Calculate total spending
    total_spent = all_orders.filter(
        status__in=['completed', 'delivered', 'confirmed']
    ).aggregate(total=Sum('order_total'))['total'] or 0
    
    # ========================= FEATURED PRODUCTS =========================
    # Get featured/new products
    try:
        products = Product.objects.filter(
            is_available=True,
            is_featured=True
        ).select_related('category').order_by('-created_date')[:12]
        
        # If not enough featured products, get recent products
        if products.count() < 6:
            products = Product.objects.filter(
                is_available=True
            ).select_related('category').order_by('-created_date')[:12]
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        products = []
    
    # ========================= RECENT ACTIVITIES =========================
    # Get recent orders (last 5)
    recent_orders = all_orders.select_related('user').order_by('-order_date')[:5]
    
    # ========================= USER PROFILE INFO =========================
    user_profile = None
    try:
        from accounts.models import Profile
        user_profile = Profile.objects.get(user=user)
    except:
        user_profile = None
    
    # ========================= CONTEXT DATA =========================
    context = {
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'total_spent': float(total_spent),
        'products': products,
        'recent_orders': recent_orders,
        'user_profile': user_profile,
        'page_title': 'Dashboard',
        'breadcrumb': 'Dashboard',
    }
    
    return render(request, 'accounts/dashboard.html', context)




@login_required
def user_profile(request):
    """
    Display and manage user profile information.
    """
    from accounts.models import Profile
    
    user = request.user
    
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
    
    if request.method == 'POST':
        # Handle profile update
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        country = request.POST.get('country', '').strip()
        
        # Update user info
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        # Update profile
        profile.phone = phone
        profile.address = address
        profile.city = city
        profile.country = country
        profile.save()
        
        from django.contrib import messages
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'user': user,
        'profile': profile,
        'page_title': 'User Profile',
        'breadcrumb': 'Profile',
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required(login_url='login')
def myOrders(request):
    """
    Display the user's order history with filtering and pagination.
    """
    user = request.user

    # Get filter parameters from the request
    status_filter = request.GET.get('status', 'all')  # Default to 'all'
    page_num = request.GET.get('page', 1)  # Default to page 1

    # Base queryset: Fetch orders for the logged-in user
    orders = Order.objects.filter(user=user).order_by('-created_at')

    # Apply status filter if provided
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)

    # Paginate the orders (10 orders per page)
    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(page_num)

    # Context data for the template
    context = {
        'page_obj': page_obj,  # Paginated orders
        'status_filter': status_filter,  # Current status filter
        'total_orders': orders.count(),  # Total number of orders
        'page_title': 'My Orders',  # Page title
        'breadcrumb': 'Orders',  # Breadcrumb for navigation
    }

    return render(request, 'accounts/myOrders.html', context)


@login_required
def order_detail(request, order_id):
    """
    Display detailed information about a specific order.
    """
    from store.models import Order
    
    user = request.user
    
    try:
        order = Order.objects.get(order_number=order_id, user=user)
        order_items = order.orderitem_set.all().select_related('product')
    except Order.DoesNotExist:
        from django.shortcuts import get_object_or_404
        order = get_object_or_404(Order, pk=order_id, user=user)
        order_items = order.orderitem_set.all().select_related('product')
    
    context = {
        'order': order,
        'order_items': order_items,
        'page_title': f'Order #{order.order_number}',
        'breadcrumb': 'Order Details',
    }
    
    return render(request, 'accounts/order_detail.html', context)


@login_required
def change_password(request):
    """
    Handle user password change requests.
    """
    if request.method == 'POST':
        from django.contrib.auth import authenticate, update_session_auth_hash
        from django.contrib import messages
        
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        user = request.user
        
        # Verify current password
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')
        
        # Validate new password
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('change_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')
        
        if new_password == current_password:
            messages.error(request, 'New password must be different from current password.')
            return redirect('change_password')
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Update session to prevent logout
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('dashboard')
    
    context = {
        'page_title': 'Change Password',
        'breadcrumb': 'Change Password',
    }
    
    return render(request, 'accounts/change_password.html', context)


@login_required
def wishlist(request):
    """
    Display user's wishlist items.
    """
    from store.models import Product
    from accounts.models import Wishlist
    
    try:
        wishlist_items = Wishlist.objects.filter(
            user=request.user
        ).select_related('product').order_by('-added_date')
    except:
        wishlist_items = []
    
    context = {
        'wishlist_items': wishlist_items,
        'total_items': len(wishlist_items),
        'page_title': 'My Wishlist',
        'breadcrumb': 'Wishlist',
    }
    
    return render(request, 'accounts/wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """
    Add or remove product from user's wishlist.
    """
    from store.models import Product
    from accounts.models import Wishlist
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    
    try:
        product = get_object_or_404(Product, id=product_id)
        
        # Check if already in wishlist
        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).first()
        
        if wishlist_item:
            # Remove from wishlist
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'action': 'removed',
                'message': 'Removed from wishlist'
            })
        else:
            # Add to wishlist
            Wishlist.objects.create(
                user=request.user,
                product=product
            )
            return JsonResponse({
                'success': True,
                'action': 'added',
                'message': 'Added to wishlist'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')


from orders.models import Order

@login_required(login_url='login')
def myOrders(request):
    orders = Order.objects.filter(user=request.user).exclude(status='pending').order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/myOrders.html', context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)






from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from orders.models import Order

@login_required
def dashboard(request):
    """
    Display comprehensive user dashboard with orders, spending, and featured products.
    Shows personalized statistics and quick access to frequently used features.
    """
    from store.models import Product
    
    user = request.user
    
    # ========================= ORDERS STATISTICS =========================
    # Get all orders for current user
    all_orders = Order.objects.filter(user=user).select_related('user')
    
    # Calculate total orders
    total_orders = all_orders.count()
    
    # Calculate completed orders
    completed_orders = all_orders.filter(
        status__in=['completed', 'delivered', 'confirmed']
    ).count()
    
    # Calculate pending orders
    pending_orders = all_orders.filter(
        status__in=['pending', 'processing', 'shipped']
    ).count()
    
    # Calculate cancelled orders
    cancelled_orders = all_orders.filter(
        status__in=['cancelled', 'failed']
    ).count()
    
    # ========================= TOTAL SPENDING CALCULATION =========================
    # Get the exact total amount spent (from completed/delivered orders)
    total_spent_data = all_orders.filter(
        status__in=['completed', 'delivered', 'confirmed']
    ).aggregate(total=Sum('total_amount'))
    
    total_spent = total_spent_data['total'] or 0
    
    # Calculate average order value
    if completed_orders > 0:
        average_order_value = total_spent / completed_orders
    else:
        average_order_value = 0
    
    # Get pending spending (orders not yet completed)
    pending_spent_data = all_orders.filter(
        status__in=['pending', 'processing', 'shipped']
    ).aggregate(total=Sum('total_amount'))
    
    pending_spent = pending_spent_data['total'] or 0
    
    # ========================= FEATURED PRODUCTS =========================
    # Get featured/new products
    try:
        products = Product.objects.filter(
            is_available=True
        ).select_related('category').order_by('-created_date')[:12]
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        products = []
    
    # ========================= RECENT ACTIVITIES =========================
    # Get recent orders (last 10)
    recent_orders = all_orders.select_related('user').order_by('-created_at')[:10]
    
    # Get orders from last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_spending_data = all_orders.filter(
        status__in=['completed', 'delivered', 'confirmed'],
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('total_amount'))
    
    recent_spending = recent_spending_data['total'] or 0
    
    # Get monthly statistics
    monthly_orders = all_orders.filter(
        created_at__year=timezone.now().year,
        created_at__month=timezone.now().month
    ).count()
    
    # ========================= USER PROFILE INFO =========================
    user_profile = None
    try:
        from accounts.models import Profile
        user_profile = Profile.objects.get(user=user)
    except:
        user_profile = None
    
    # ========================= ORDER BREAKDOWN =========================
    # Get order status breakdown for pie chart
    status_breakdown = all_orders.values('status').annotate(count=Count('id')).order_by('-count')
    
    # ========================= TOP PRODUCTS =========================
    # Get top purchased products
    try:
        from orders.models import OrderItem
        top_products = OrderItem.objects.filter(
            order__user=user
        ).values('product__product_name', 'product__id').annotate(
            total_quantity=Sum('quantity'),
            total_spent=Sum('price')
        ).order_by('-total_quantity')[:5]
    except:
        top_products = []
    
    # ========================= CONTEXT DATA =========================
    context = {
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'cancelled_orders': cancelled_orders,
        'total_spent': float(total_spent),
        'pending_spent': float(pending_spent),
        'average_order_value': float(average_order_value),
        'recent_spending': float(recent_spending),
        'monthly_orders': monthly_orders,
        'products': products,
        'recent_orders': recent_orders,
        'user_profile': user_profile,
        'status_breakdown': status_breakdown,
        'top_products': top_products,
        'page_title': 'Dashboard',
        'breadcrumb': 'Dashboard',
    }
    
    return render(request, 'accounts/dashboard.html', context)









from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from store.models import Product, Category
from orders.models import Order
from django.contrib.auth import get_user_model

@login_required
def customerDashboard(request):
    products = Product.objects.all()[:6]
    categories = Category.objects.all()
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    orders_recent = orders[:5]
    active_orders = Order.objects.filter(user=request.user).exclude(status='pending').order_by('-created_at')
    context = {
        'products': products,
        'categories': categories,
        'orders': orders_recent,
        'active_orders': active_orders,
        'user': request.user,
    }
    return render(request, 'accounts/customerDashboard.html', context)

@login_required
def user_management(request):
    users = Account.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'accounts/user_management.html', context)


from .forms import ContactForm
from .models import ContactMessage

@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.user = request.user
            contact_message.save()
            messages.success(request, 'Your message has been sent to the admin.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'accounts/contact.html', {'form': form})


@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Set a custom message based on order status
    if order.status.lower() == "completed":
        order_message = "Your order has been completed. Thank you for shopping with us!"
    elif order.status.lower() == "delivered":
        order_message = "Your order has been delivered. Enjoy your treats!"
    else:
        order_message = "Your order is being processed. You will receive a notification when it is ready or dispatched."
    context = {
        'order': order,
        'order_message': order_message,
    }
    return render(request, 'accounts/track_order.html', context)


from .models import Transaction  # Adjust import path if model is in orders.models

@login_required
def transactions(request):
    transactions = Transaction.objects.filter(order__user=request.user).order_by('-created_at')
    context = {
        'transactions': transactions,
    }
    return render(request, 'accounts/transactions.html', context)

def recipes(request):
    return render(request, 'accounts/recipes.html')

from .forms import ContactForm
from .models import ContactMessage
from django.contrib.auth.decorators import login_required
@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.user = request.user
            contact_message.save()
            messages.success(request, 'Your message has been sent to the admin.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'accounts/contact.html', {'form': form})

from .models import Wishlist
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'accounts/wishlist.html', context)


def about(request):
    return render(request, 'accounts/about.html')

@login_required
def account(request):
    userprofile = getattr(request.user, 'userprofile', None)
    context = {
        'user': request.user,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/account.html', context)

from store.models import Product
@login_required
def products(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'accounts/products.html', context)



from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

@admin_required
def admin_dashboard(request):
    User = get_user_model()
    registered_users = User.objects.all()
    return render(request, 'accounts/admin_dashboard.html', {
        'registered_users': registered_users,
    })

@admin_required
def contact_messages(request):
    # Fetch contact messages from your model
    # messages = ContactMessage.objects.all()
    return render(request, 'accounts/contact_messages.html')  # Pass messages in context

@admin_required
def cart_list(request):
    # carts = Cart.objects.all()
    return render(request, 'accounts/cart_list.html')

@admin_required
def cart_items(request):
    # items = CartItem.objects.all()
    return render(request, 'accounts/cart_items.html')

@admin_required
def category_list(request):
    # categories = Category.objects.all()
    return render(request, 'accounts/category_list.html')

@admin_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')  # Fetch all orders, newest first
    return render(request, 'accounts/order_list.html', {'orders': orders})

@admin_required
def payment_list(request):
    # payments = Payment.objects.all()
    return render(request, 'accounts/payment_list.html')

@admin_required
def product_list(request):
    # products = Product.objects.all()
    return render(request, 'accounts/product_list.html')

@admin_required
def variation_list(request):
    # variations = Variation.objects.all()
    return render(request, 'accounts/variation_list.html')

# CDMIS sections
@admin_required
def group_list(request):
    # groups = Group.objects.all()
    return render(request, 'accounts/group_list.html')

@admin_required
def activity_list(request):
    # activities = Activity.objects.all()
    return render(request, 'accounts/activity_list.html')

@admin_required
def service_list(request):
    # services = Service.objects.all()
    return render(request, 'accounts/service_list.html')

@admin_required
def training_list(request):
    # trainings = Training.objects.all()
    return render(request, 'accounts/training_list.html')

@login_required
def profile(request):
    userprofile = getattr(request.user, 'userprofile', None)
    context = {
        'user': request.user,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def dashboard(request):
    # Add any context data you want to show on the dashboard
    orders_count = Order.objects.filter(user=request.user).count()
    products = Product.objects.all()[:6]
    categories = Category.objects.all()
    userprofile = getattr(request.user, 'userprofile', None)
    context = {
        'orders_count': orders_count,
        'products': products,
        'categories': categories,
        'user': request.user,
        'userprofile': userprofile,
        
    }
    return render(request, 'accounts/dashboard.html', context)


from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

@admin_required
def users_view(request):
    User = get_user_model()
    users = User.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, pk=user_id)
        if action == 'activate':
            user.is_active = True
            user.save()
            messages.success(request, f'User {user.username} activated.')
        elif action == 'deactivate':
            user.is_active = False
            user.save()
            messages.success(request, f'User {user.username} deactivated.')
        elif action == 'delete':
            user.delete()
            messages.success(request, f'User deleted.')
        return redirect('users')
    return render(request, 'accounts/users.html', {'users': users})


from django.shortcuts import render, redirect
from .forms import CategoryForm

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')  # or wherever you want to redirect
    else:
        form = CategoryForm()
    return render(request, 'accounts/add_category.html', {'form': form})




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Payment
from .forms import PaymentForm

@login_required
def finance_dashboard(request):
    if not request.user.role == 'finance':
        return redirect('dashboard')
    payments = Payment.objects.filter(created_by=request.user)
    return render(request, 'finance/dashboard.html', {'payments': payments})

# ...existing code...
from django.contrib.auth.models import Group
from decimal import Decimal, InvalidOperation

@login_required
def add_payment(request):
    """
    Finance-only view to add a payment.
    - Passes available groups to the template for selection.
    - Expects POST: group_id (optional), amount, description.
    - If Payment model has a 'group' FK, it will be set. Otherwise the group name is prepended to the description.
    """
    if not getattr(request.user, 'role', None) == 'finance':
        return redirect('dashboard')

    groups = Group.objects.all()

    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        amount_raw = request.POST.get('amount', '').strip()
        description = request.POST.get('description', '').strip()

        # validate amount
        try:
            amount = Decimal(amount_raw)
            if amount <= 0:
                raise InvalidOperation()
        except (InvalidOperation, TypeError):
            messages.error(request, 'Please enter a valid positive amount.')
            return render(request, 'finance/add_payment.html', {
                'groups': groups,
                'amount': amount_raw,
                'description': description,
            })

        # create Payment instance
        payment = Payment.objects.create(amount=10.00, description='Test', created_by=user)

        # attach group if model supports it, otherwise include group in description
        if group_id:
            try:
                group = Group.objects.get(pk=group_id)
            except Group.DoesNotExist:
                messages.error(request, 'Selected group not found.')
                return render(request, 'finance/add_payment.html', {
                    'groups': groups,
                    'amount': amount_raw,
                    'description': description,
                })

            if hasattr(payment, 'group'):
                payment.group = group
            else:
                # prepend group info to description to preserve association
                payment.description = f"[Group: {group.name}] {payment.description}"

        payment.save()
        messages.success(request, 'Payment added successfully.')
        return redirect('finance_dashboard')

    # GET -> show form with groups
    return render(request, 'finance/add_payment.html', {'groups': groups})
# ...existing code...


from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import RegistrationForm, UserForm

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

@admin_required
def user_management(request):
    User = get_user_model()
    users = User.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        if action == 'activate':
            user.is_active = True
            user.save()
            messages.success(request, f'User {user.username} activated.')
        elif action == 'deactivate':
            user.is_active = False
            user.save()
            messages.success(request, f'User {user.username} deactivated.')
        elif action == 'delete':
            user.delete()
            messages.success(request, f'User deleted.')
        elif action == 'change_role':
            new_role = request.POST.get('new_role')
            user.role = new_role
            user.save()
            messages.success(request, f'User {user.username} role changed to {new_role}.')
        return redirect('user_management')
    return render(request, 'accounts/user_management.html', {'users': users})

@admin_required
def add_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User added successfully.')
            return redirect('user_management')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/add_user.html', {'form': form})

@admin_required
def user_detail(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'activate':
            user.is_active = True
            user.save()
            messages.success(request, f'User {user.username} activated.')
        elif action == 'deactivate':
            user.is_active = False
            user.save()
            messages.success(request, f'User {user.username} deactivated.')
        elif action == 'delete':
            user.delete()
            messages.success(request, f'User deleted.')
            return redirect('user_management')
        elif action == 'change_role':
            new_role = request.POST.get('new_role')
            user.role = new_role
            user.save()
            messages.success(request, f'User {user.username} role changed to {new_role}.')
        return redirect('user_detail', user_id=user.id)
    return render(request, 'accounts/user_detail.html', {'user_obj': user})


# accounts/views.py
from django.contrib.auth.decorators import login_required

@login_required
def redirect_after_login(request):
    if request.user.role == 'finance':
        return redirect('finance_dashboard')
    return redirect('dashboard')




@login_required
def accademicWrittings(request):
    """
    Display academic writings/articles page for authenticated users.
    Allows users to browse, search, and filter academic articles.
    """
    from django.db.models import Q
    from django.core.paginator import Paginator
    
    # Get search query and filter parameters
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'recent')
    category = request.GET.get('category', 'all')
    page_num = request.GET.get('page', 1)
    
    # Example articles data - can be replaced with database model queries
    # This is mock data for demonstration
    articles = [
        {
            'id': 1,
            'title': 'Building Sustainable Business Models for the African Market',
            'author': 'Bramwel Nyongesa',
            'author_initials': 'BN',
            'date': '2024-11-15',
            'category': 'Business',
            'description': 'Learn key strategies for creating sustainable business models that resonate with African markets. Discover how to balance profitability with social impact.',
            'views': 2400,
            'likes': 156,
            'read_time': 8,
        },
        {
            'id': 2,
            'title': 'AI & Machine Learning: Transforming Retail Operations',
            'author': 'Diana Nambuchi',
            'author_initials': 'DN',
            'date': '2024-11-12',
            'category': 'Technology',
            'description': 'Explore how artificial intelligence and machine learning are revolutionizing retail operations. From inventory management to personalized customer experiences.',
            'views': 3800,
            'likes': 298,
            'read_time': 12,
        },
        {
            'id': 3,
            'title': 'Digital Payment Solutions: The Future of Commerce',
            'author': 'Assumpta Sikolia',
            'author_initials': 'AS',
            'date': '2024-11-10',
            'category': 'Innovation',
            'description': 'Understanding the role of digital payments in shaping the future of e-commerce. Security, innovation, and customer adoption strategies.',
            'views': 1900,
            'likes': 127,
            'read_time': 10,
        },
        {
            'id': 4,
            'title': 'Consumer Behavior Trends in Online Shopping 2024',
            'author': 'Bramwel Nyongesa',
            'author_initials': 'BN',
            'date': '2024-11-08',
            'category': 'Market Research',
            'description': 'Comprehensive analysis of consumer behavior patterns in 2024. What drives purchases, payment preferences, and customer loyalty in online retail.',
            'views': 5200,
            'likes': 412,
            'read_time': 15,
        },
        {
            'id': 5,
            'title': 'Cybersecurity Best Practices for E-Commerce Platforms',
            'author': 'Diana Nambuchi',
            'author_initials': 'DN',
            'date': '2024-11-05',
            'category': 'Security',
            'description': 'Essential security measures every e-commerce platform must implement. From data encryption to fraud prevention strategies.',
            'views': 3100,
            'likes': 234,
            'read_time': 11,
        },
        {
            'id': 6,
            'title': 'Creating Exceptional Customer Experiences in Digital Retail',
            'author': 'Assumpta Sikolia',
            'author_initials': 'AS',
            'date': '2024-11-01',
            'category': 'Customer Experience',
            'description': 'Strategies for delivering exceptional customer experiences online. From personalization to responsive support systems.',
            'views': 2700,
            'likes': 189,
            'read_time': 9,
        },
        {
            'id': 7,
            'title': 'The Future of E-Commerce in Africa',
            'author': 'Bramwel Nyongesa',
            'author_initials': 'BN',
            'date': '2024-10-28',
            'category': 'Business',
            'description': 'Explore how digital transformation is reshaping the retail landscape across Africa, and what entrepreneurs need to know to stay competitive.',
            'views': 4100,
            'likes': 356,
            'read_time': 13,
        },
        {
            'id': 8,
            'title': 'Logistics & Supply Chain Optimization',
            'author': 'Diana Nambuchi',
            'author_initials': 'DN',
            'date': '2024-10-25',
            'category': 'Technology',
            'description': 'Modern approaches to supply chain management using technology and data analytics to improve efficiency and reduce costs.',
            'views': 2900,
            'likes': 201,
            'read_time': 14,
        },
    ]
    
    # Filter by search query
    if search_query:
        articles = [
            a for a in articles
            if search_query.lower() in a['title'].lower()
            or search_query.lower() in a['description'].lower()
            or search_query.lower() in a['author'].lower()
        ]
    
    # Filter by category
    if category != 'all':
        articles = [a for a in articles if a['category'].lower() == category.lower()]
    
    # Sort articles
    if sort_by == 'popular':
        articles = sorted(articles, key=lambda x: x['views'], reverse=True)
    elif sort_by == 'trending':
        articles = sorted(articles, key=lambda x: x['likes'], reverse=True)
    elif sort_by == 'oldest':
        articles = sorted(articles, key=lambda x: x['date'])
    else:  # recent (default)
        articles = sorted(articles, key=lambda x: x['date'], reverse=True)
    
    # Pagination
    paginator = Paginator(articles, 6)  # 6 articles per page
    page_obj = paginator.get_page(page_num)
    
    # Get unique categories for filter dropdown
    categories = sorted(list(set([a['category'] for a in articles])))
    
    # Statistics
    stats = {
        'total_articles': len(articles),
        'total_authors': 3,
        'monthly_readers': '50K+',
        'total_categories': 8,
    }
    
    context = {
        'page_obj': page_obj,
        'articles': page_obj.object_list,
        'categories': categories,
        'search_query': search_query,
        'sort_by': sort_by,
        'selected_category': category,
        'stats': stats,
        'total_articles': len(articles),
    }
    
    return render(request, 'accounts/accademicWrittings.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin')

@login_required
@user_passes_test(is_admin)
def userManagement(request):
    """
    Display and manage users with search, filter, and pagination.
    Only accessible to admin users.
    """
    # Get search and filter parameters
    search_query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()
    page_num = request.GET.get('page', 1)
    
    # Base queryset
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    
    # Search by name or email
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by role
    if role_filter:
        users = users.filter(profile__role=role_filter)
    
    # Pagination
    paginator = Paginator(users, 10)  # 10 users per page
    page_obj = paginator.get_page(page_num)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'roles': ['customer', 'staff', 'admin'],
    }
    
    return render(request, 'accounts/userManagement.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def user_create(request):
    """
    Create a new user via modal form.
    """
    try:
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', 'customer')
        
        # Validation
        if not username or not email:
            messages.error(request, 'Username and email are required.')
            return redirect('accounts:userManagement')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
            return redirect('accounts:userManagement')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, f'Email "{email}" already exists.')
            return redirect('accounts:userManagement')
        
        if not password or len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return redirect('accounts:userManagement')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Set full name
        if full_name:
            parts = full_name.split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
            user.save()
        
        # Set admin/staff permissions
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        elif role == 'staff':
            user.is_staff = True
        user.save()
        
        # Create or update profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        
        messages.success(request, f'User "{username}" created successfully.')
        return redirect('accounts:userManagement')
        
    except Exception as e:
        messages.error(request, f'Error creating user: {str(e)}')
        return redirect('accounts:userManagement')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def user_update(request, user_id):
    """
    Update an existing user via modal form.
    """
    try:
        user = get_object_or_404(User, id=user_id)
        
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', 'customer')
        
        # Validation
        if not username or not email:
            messages.error(request, 'Username and email are required.')
            return redirect('accounts:userManagement')
        
        # Check if username already exists (excluding current user)
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, f'Username "{username}" already exists.')
            return redirect('accounts:userManagement')
        
        # Check if email already exists (excluding current user)
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request, f'Email "{email}" already exists.')
            return redirect('accounts:userManagement')
        
        # Update user
        user.username = username
        user.email = email
        
        # Update full name
        if full_name:
            parts = full_name.split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
        else:
            user.first_name = ''
            user.last_name = ''
        
        # Update password if provided
        if password:
            if len(password) < 6:
                messages.error(request, 'Password must be at least 6 characters long.')
                return redirect('accounts:userManagement')
            user.set_password(password)
        
        # Update admin/staff permissions
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        elif role == 'staff':
            user.is_superuser = False
            user.is_staff = True
        else:  # customer
            user.is_superuser = False
            user.is_staff = False
        
        user.save()
        
        # Update profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        
        messages.success(request, f'User "{username}" updated successfully.')
        return redirect('accounts:userManagement')
        
    except Exception as e:
        messages.error(request, f'Error updating user: {str(e)}')
        return redirect('accounts:userManagement')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def user_delete(request, user_id):
    """
    Delete a user.
    """
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Prevent self-deletion
        if user.id == request.user.id:
            messages.error(request, 'You cannot delete your own account.')
            return redirect('accounts:userManagement')
        
        username = user.username
        user.delete()
        
        messages.success(request, f'User "{username}" deleted successfully.')
        return redirect('accounts:userManagement')
        
    except Exception as e:
        messages.error(request, f'Error deleting user: {str(e)}')
        return redirect('accounts:userManagement')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from store.models import Product, Variation
from django.http import JsonResponse

def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def store_variation(request):
    """
    Manage product variations (add, view, edit, delete).
    Admin-only view for managing product sizes, colors, and other variations.
    """
    # Get filter and search parameters
    search_query = request.GET.get('q', '').strip()
    product_filter = request.GET.get('product', '').strip()
    page_num = request.GET.get('page', 1)
    
    # Base queryset
    variations = Variation.objects.all().select_related('product').order_by('-id')
    
    # Search by product name or variation name
    if search_query:
        variations = variations.filter(
            Q(product__product_name__icontains=search_query) |
            Q(variation_category__icontains=search_query) |
            Q(variation_value__icontains=search_query)
        )
    
    # Filter by product
    if product_filter:
        variations = variations.filter(product__id=product_filter)
    
    # Pagination
    paginator = Paginator(variations, 15)  # 15 variations per page
    page_obj = paginator.get_page(page_num)
    
    # Get all products for filter dropdown
    products = Product.objects.all().values('id', 'product_name').order_by('product_name')
    
    # Statistics
    stats = {
        'total_variations': Variation.objects.count(),
        'products_with_variations': Variation.objects.values('product').distinct().count(),
        'variation_categories': Variation.objects.values('variation_category').distinct().count(),
    }
    
    context = {
        'page_obj': page_obj,
        'variations': page_obj.object_list,
        'products': products,
        'search_query': search_query,
        'product_filter': product_filter,
        'stats': stats,
        'page_title': 'Product Variations',
        'breadcrumb': 'Variations',
    }
    
    return render(request, 'accounts/store_variation.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def variation_create(request):
    """
    Create a new product variation via AJAX/modal.
    """
    try:
        product_id = request.POST.get('product_id', '').strip()
        category = request.POST.get('category', '').strip()
        value = request.POST.get('value', '').strip()
        price = request.POST.get('price', '0')
        
        # Validation
        if not product_id or not category or not value:
            return JsonResponse({
                'success': False,
                'error': 'Product, category, and value are required.'
            }, status=400)
        
        # Get product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Product not found.'
            }, status=404)
        
        # Check for duplicate variation
        if Variation.objects.filter(
            product=product,
            variation_category=category,
            variation_value=value
        ).exists():
            return JsonResponse({
                'success': False,
                'error': f'This {category} variation already exists for this product.'
            }, status=400)
        
        # Create variation
        variation = Variation.objects.create(
            product=product,
            variation_category=category,
            variation_value=value,
            variation_price=price if price else 0
        )
        
        messages.success(request, f'Variation "{value}" added successfully.')
        
        return JsonResponse({
            'success': True,
            'message': f'Variation "{value}" created successfully.',
            'variation_id': variation.id,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def variation_update(request, variation_id):
    """
    Update an existing product variation.
    """
    try:
        variation = get_object_or_404(Variation, id=variation_id)
        
        category = request.POST.get('category', '').strip()
        value = request.POST.get('value', '').strip()
        price = request.POST.get('price', '0')
        
        # Validation
        if not category or not value:
            return JsonResponse({
                'success': False,
                'error': 'Category and value are required.'
            }, status=400)
        
        # Check for duplicate (excluding current variation)
        if Variation.objects.filter(
            product=variation.product,
            variation_category=category,
            variation_value=value
        ).exclude(id=variation_id).exists():
            return JsonResponse({
                'success': False,
                'error': f'This {category} variation already exists for this product.'
            }, status=400)
        
        # Update variation
        old_value = variation.variation_value
        variation.variation_category = category
        variation.variation_value = value
        variation.variation_price = price if price else 0
        variation.save()
        
        messages.success(request, f'Variation "{old_value}" updated to "{value}" successfully.')
        
        return JsonResponse({
            'success': True,
            'message': f'Variation updated successfully.',
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST", "DELETE"])
def variation_delete(request, variation_id):
    """
    Delete a product variation.
    """
    try:
        variation = get_object_or_404(Variation, id=variation_id)
        
        value = variation.variation_value
        category = variation.variation_category
        variation.delete()
        
        messages.success(request, f'{category} variation "{value}" deleted successfully.')
        
        return JsonResponse({
            'success': True,
            'message': f'Variation deleted successfully.',
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_admin)
def variation_by_product(request, product_id):
    """
    Get all variations for a specific product (AJAX endpoint).
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        variations = Variation.objects.filter(product=product).values(
            'id', 'variation_category', 'variation_value', 'variation_price'
        )
        
        return JsonResponse({
            'success': True,
            'variations': list(variations),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)



def category_list(request):
    # categories = Category.objects.all()
    return render(request, 'accounts/category_list.html')


def resendOTP(request):
    # Your OTP resend logic here
    return redirect('forgotPassword')




import random
import string
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

# ========================= OTP GENERATION & STORAGE =========================

def generate_otp(length=6):
    """
    Generate a random 6-digit OTP.
    """
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(request, user_email, otp):
    """
    Send OTP to user's email address with proper error handling.
    """
    try:
        # Get current site
        current_site = get_current_site(request)
        
        # Prepare email context
        context = {
            'otp': otp,
            'email': user_email,
            'domain': current_site.domain,
            'expiry_time': 10,  # 10 minutes
            'site_name': 'BESTSTORE',
        }
        
        # Render email template
        try:
            message_html = render_to_string('accounts/otp_email.html', context)
        except Exception as template_error:
            logger.error(f"Template rendering error: {str(template_error)}")
            # Fallback to plain text email if template fails
            message_html = f"""
            <html>
                <body>
                    <h2>Password Reset OTP</h2>
                    <p>Your OTP code is: <strong>{otp}</strong></p>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </body>
            </html>
            """
        
        # Send email
        email = EmailMessage(
            subject='Your Password Reset OTP - BESTSTORE',
            body=message_html,
            from_email='noreply@beststore.com',  # Change to your email
            to=[user_email]
        )
        email.content_subtype = 'html'
        
        # Try sending
        result = email.send(fail_silently=False)
        
        logger.info(f"OTP email sent successfully to {user_email}. Result: {result}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending OTP email to {user_email}: {str(e)}")
        print(f"DEBUG - Email sending error: {str(e)}")
        return False


# ========================= FORGOT PASSWORD - STEP 1 =========================

def forgotPassword(request):
    """
    Step 1: User enters email to receive OTP.
    Generates OTP and sends it via email.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # Validate email format
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'accounts/forgotPassword.html')
        
        # Basic email format validation
        if '@' not in email or '.' not in email:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'accounts/forgotPassword.html')
        
        # Check if user exists
        try:
            from accounts.models import Account
            user = Account.objects.get(email__exact=email)
        except Account.DoesNotExist:
            # Security: Don't reveal if account exists
            messages.info(request, f'If an account exists with {email}, you will receive an OTP email.')
            return render(request, 'accounts/forgotPassword.html')
        
        # Check if user is active
        if not user.is_active:
            messages.error(request, 'This account has been deactivated. Please contact support.')
            return render(request, 'accounts/forgotPassword.html')
        
        # Generate OTP
        otp = generate_otp()
        logger.info(f"Generated OTP for {email}: {otp}")
        
        # Store OTP in cache with 10-minute expiration
        cache_key = f'otp_{email}'
        cache.set(cache_key, {
            'otp': otp,
            'attempts': 0,
            'created_at': datetime.now().isoformat(),
        }, timeout=600)  # 10 minutes
        
        # Send OTP via email
        if send_otp_email(request, email, otp):
            messages.success(request, f'OTP has been sent to {email}. It will expire in 10 minutes.')
            
            # Store email in session for next step
            request.session['forgot_password_email'] = email
            request.session['otp_sent_time'] = datetime.now().isoformat()
            
            return redirect('verify_otp')
        else:
            messages.error(request, 'Failed to send OTP. Please check your email address or try again later.')
            logger.error(f"Failed to send OTP to {email}")
            return render(request, 'accounts/forgotPassword.html', {
                'email': email,
            })
    
    return render(request, 'accounts/forgotPassword.html')


# ========================= VERIFY OTP - STEP 2 =========================

def verify_otp(request):
    """
    Step 2: User enters OTP received in email.
    Validates OTP and allows password reset if valid.
    """
    # Check if email is in session
    email = request.session.get('forgot_password_email')
    if not email:
        messages.error(request, 'Please start the password reset process again.')
        return redirect('forgotPassword')
    
    if request.method == 'POST':
        # Get OTP from form (6 separate digit inputs or single input)
        otp_input = request.POST.get('otp', '').strip()
        
        # If OTP comes as separate digits, combine them
        if not otp_input:
            otp_digits = [
                request.POST.get(f'otp_{i}', '') for i in range(6)
            ]
            otp_input = ''.join(otp_digits)
        
        logger.info(f"OTP verification attempt for {email}: {otp_input}")
        
        # Validate OTP input
        if not otp_input or len(otp_input) != 6 or not otp_input.isdigit():
            messages.error(request, 'Please enter a valid 6-digit OTP.')
            return render(request, 'accounts/verify_otp.html', {
                'email': email,
                'page_title': 'Verify OTP',
                'breadcrumb': 'Verify OTP',
            })
        
        # Get OTP from cache
        cache_key = f'otp_{email}'
        otp_data = cache.get(cache_key)
        
        # Check if OTP exists and hasn't expired
        if not otp_data:
            messages.error(request, 'OTP has expired. Please request a new one.')
            request.session.pop('forgot_password_email', None)
            return redirect('forgotPassword')
        
        stored_otp = otp_data.get('otp')
        attempts = otp_data.get('attempts', 0)
        
        # Check attempt limit (max 5 attempts)
        if attempts >= 5:
            cache.delete(cache_key)
            messages.error(request, 'Maximum OTP attempts exceeded. Please request a new OTP.')
            request.session.pop('forgot_password_email', None)
            logger.warning(f"Max OTP attempts exceeded for {email}")
            return redirect('forgotPassword')
        
        # Verify OTP
        if otp_input == stored_otp:
            # OTP verified successfully
            logger.info(f"OTP verified successfully for {email}")
            
            # Store in session for password reset
            request.session['otp_verified'] = True
            request.session['otp_verified_email'] = email
            
            # Delete OTP from cache
            cache.delete(cache_key)
            
            messages.success(request, 'OTP verified successfully. Please set your new password.')
            return redirect('resetPassword')
        else:
            # Incorrect OTP
            attempts += 1
            otp_data['attempts'] = attempts
            cache.set(cache_key, otp_data, timeout=600)
            
            remaining_attempts = 5 - attempts
            logger.warning(f"Incorrect OTP for {email}. Attempts: {attempts}")
            
            if remaining_attempts > 0:
                messages.error(request, f'Incorrect OTP. {remaining_attempts} attempts remaining.')
            else:
                messages.error(request, 'Maximum OTP attempts exceeded. Please request a new OTP.')
                request.session.pop('forgot_password_email', None)
                return redirect('forgotPassword')
            
            return render(request, 'accounts/verify_otp.html', {
                'email': email,
                'attempts': attempts,
                'remaining_attempts': remaining_attempts,
                'page_title': 'Verify OTP',
                'breadcrumb': 'Verify OTP',
            })
    
    context = {
        'email': email,
        'page_title': 'Verify OTP',
        'breadcrumb': 'Verify OTP',
    }
    return render(request, 'accounts/verify_otp.html', context)


# ========================= RESEND OTP =========================

def resendOTP(request):
    """
    Resend OTP to user's email with rate limiting.
    """
    email = request.session.get('forgot_password_email')
    
    if not email:
        messages.error(request, 'Please start the password reset process again.')
        return redirect('forgotPassword')
    
    # Check rate limiting (only resend after 30 seconds)
    resend_key = f'otp_resend_{email}'
    if cache.get(resend_key):
        messages.warning(request, 'Please wait 30 seconds before requesting a new OTP.')
        return redirect('verify_otp')
    
    try:
        # Get user
        from accounts.models import Account
        user = Account.objects.get(email__exact=email)
        
        # Generate new OTP
        otp = generate_otp()
        logger.info(f"Resending OTP for {email}: {otp}")
        
        # Store OTP in cache
        cache_key = f'otp_{email}'
        cache.set(cache_key, {
            'otp': otp,
            'attempts': 0,
            'created_at': datetime.now().isoformat(),
        }, timeout=600)
        
        # Set resend rate limit (30 seconds)
        cache.set(resend_key, True, timeout=30)
        
        # Send OTP via email
        if send_otp_email(request, email, otp):
            messages.success(request, f'New OTP has been sent to {email}.')
            logger.info(f"OTP resent successfully to {email}")
        else:
            messages.error(request, 'Failed to send OTP. Please try again.')
            logger.error(f"Failed to resend OTP to {email}")
        
        return redirect('verify_otp')
    
    except Account.DoesNotExist:
        messages.error(request, 'User not found.')
        logger.error(f"User not found for email: {email}")
        return redirect('forgotPassword')


# ========================= RESET PASSWORD - STEP 3 =========================

def resetPassword(request):
    """
    Step 3: User sets new password after OTP verification.
    """
    # Check if OTP is verified
    if not request.session.get('otp_verified'):
        messages.error(request, 'Please verify OTP first.')
        return redirect('verify_otp')
    
    email = request.session.get('otp_verified_email')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validation
        if not new_password or not confirm_password:
            messages.error(request, 'Please fill in all password fields.')
            return render(request, 'accounts/resetPassword.html')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'accounts/resetPassword.html')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/resetPassword.html')
        
        # Check password strength
        has_upper = any(c.isupper() for c in new_password)
        has_lower = any(c.islower() for c in new_password)
        has_digit = any(c.isdigit() for c in new_password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in new_password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            messages.error(request, 'Password must contain uppercase, lowercase, number, and special character.')
            return render(request, 'accounts/resetPassword.html')
        
        try:
            # Get user and update password
            from accounts.models import Account
            user = Account.objects.get(email__exact=email)
            user.set_password(new_password)
            user.save()
            
            logger.info(f"Password reset successfully for {email}")
            
            # Clear session data
            request.session.pop('forgot_password_email', None)
            request.session.pop('otp_verified', None)
            request.session.pop('otp_verified_email', None)
            request.session.pop('otp_sent_time', None)
            
            messages.success(request, 'Password reset successfully. Please login with your new password.')
            return redirect('login')
        
        except Account.DoesNotExist:
            messages.error(request, 'User not found.')
            logger.error(f"User not found during password reset: {email}")
            return redirect('forgotPassword')
        except Exception as e:
            messages.error(request, f'Error resetting password: {str(e)}')
            logger.error(f"Error resetting password for {email}: {str(e)}")
            return render(request, 'accounts/resetPassword.html')
    
    context = {
        'email': email,
        'page_title': 'Reset Password',
        'breadcrumb': 'Reset Password',
    }
    return render(request, 'accounts/resetPassword.html', context)


# ========================= AJAX ENDPOINTS FOR OTP =========================

def verify_otp_ajax(request):
    """
    AJAX endpoint for real-time OTP verification.
    Returns JSON response for frontend validation.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
    try:
        data = json.loads(request.body)
        otp_input = data.get('otp', '').strip()
        email = request.session.get('forgot_password_email')
        
        if not email:
            return JsonResponse({'success': False, 'error': 'Email not found in session'}, status=400)
        
        if not otp_input or len(otp_input) != 6 or not otp_input.isdigit():
            return JsonResponse({'success': False, 'error': 'Invalid OTP format'}, status=400)
        
        # Get OTP from cache
        cache_key = f'otp_{email}'
        otp_data = cache.get(cache_key)
        
        if not otp_data:
            return JsonResponse({'success': False, 'error': 'OTP expired'}, status=400)
        
        stored_otp = otp_data.get('otp')
        attempts = otp_data.get('attempts', 0)
        
        if attempts >= 5:
            cache.delete(cache_key)
            return JsonResponse({
                'success': False,
                'error': 'Maximum attempts exceeded',
                'expired': True
            }, status=400)
        
        if otp_input == stored_otp:
            # Mark as verified
            request.session['otp_verified'] = True
            request.session['otp_verified_email'] = email
            cache.delete(cache_key)
            
            return JsonResponse({
                'success': True,
                'message': 'OTP verified successfully',
                'redirect': 'resetPassword'
            })
        else:
            attempts += 1
            otp_data['attempts'] = attempts
            cache.set(cache_key, otp_data, timeout=600)
            remaining = 5 - attempts
            
            return JsonResponse({
                'success': False,
                'error': f'Incorrect OTP. {remaining} attempts remaining',
                'attempts': attempts
            }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"AJAX OTP verification error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def check_otp_expiry(request):
    """
    AJAX endpoint to check if OTP has expired.
    Returns remaining time in seconds.
    """
    email = request.session.get('forgot_password_email')
    
    if not email:
        return JsonResponse({'expired': True, 'remaining_time': 0})
    
    cache_key = f'otp_{email}'
    
    # Try to get remaining time from cache
    try:
        ttl = cache.ttl(cache_key) if hasattr(cache, 'ttl') else None
    except:
        ttl = None
    
    if ttl is None or ttl <= 0:
        return JsonResponse({'expired': True, 'remaining_time': 0})
    
    return JsonResponse({'expired': False, 'remaining_time': ttl})


