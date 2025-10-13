from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm
from .models import Account
from orders.models import Order, OrderProduct
from .forms import RegistrationForm, UserForm
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
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            
            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address [rathan.kumar@gmail.com]. Please verify it.')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
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
        identifier = request.POST.get('email') or request.POST.get('username') or ''
        password = request.POST.get('password') or ''

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
            messages.success(request, 'You are now logged in.')

            role = getattr(user, 'role', None)
            # Strict role-based redirect
            if role == 'finance':
                return redirect('finance_dashboard')
            if user.is_staff or user.is_superuser or role == 'admin':
                return redirect('admin_dashboard')
            return redirect('dashboard')

        messages.error(request, 'Invalid login credentials')
        return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
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
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    orders_count = orders.count()
    userprofile = getattr(request.user, 'userprofile', None)
    context = {
        'orders_count': orders_count,
        'orders': orders,
        'user': request.user,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


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
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
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



from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request):
    # Add any context data you want to show on the dashboard
    orders_count = Order.objects.filter(user=request.user).count()
    userprofile = getattr(request.user, 'userprofile', None)
    context = {
        'orders_count': orders_count,
        'user': request.user,
        'userprofile': userprofile,
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
        payment = Payment(amount=amount, description=description, created_by=request.user)

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