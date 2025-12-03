from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from carts.models import CartItem, Cart
from store.models import Product
from .models import Order, OrderItem
from datetime import datetime
import json
import csv


@csrf_exempt
def placeOrder(request):
    """Place a new order from checkout"""
    try:
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address_line_1 = request.POST.get('address_line_1', '').strip()
        address_line_2 = request.POST.get('address_line_2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        country = request.POST.get('country', '').strip()
        payment_method = request.POST.get('payment_method', 'mpesa').strip()
        order_note = request.POST.get('order_note', '').strip()

        # Validate required fields
        required_fields = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email address',
            'phone': 'Phone number',
            'address_line_1': 'Address',
            'city': 'City',
            'state': 'State',
            'country': 'Country'
        }

        missing_fields = []
        for field, label in required_fields.items():
            if not locals().get(field):
                missing_fields.append(label)

        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': f'Please fill in: {", ".join(missing_fields)}'
            }, status=400)

        # Validate email format
        if '@' not in email or '.' not in email.split('@')[1]:
            return JsonResponse({
                'success': False,
                'error': 'Please enter a valid email address'
            }, status=400)

        # Get cart items
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        try:
            cart = Cart.objects.get(cart_id=session_key)
            cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Your cart is empty. Please add items before ordering.'
                }, status=400)
        except Cart.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Cart not found. Please try again.'
            }, status=400)

        # Create order
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            country=country,
            payment_method=payment_method,
            order_note=order_note,
            status='pending'
        )

        # Associate with user if logged in
        if request.user.is_authenticated:
            order.user = request.user
            order.save()

        # Create order items from cart
        total_amount = 0
        for item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            total_amount += order_item.get_total_price()

        # Update order total
        order.total_amount = total_amount
        order.save()

        # Clear cart
        cart_items.delete()

        # Send confirmation email
        try:
            subject = f'Order Confirmation - Order #{order.pk}'
            html_message = render_to_string('orders/order_confirmation_email.html', {
                'order': order,
                'items': order.items.all()
            })
            email_msg = EmailMessage(
                subject,
                html_message,
                'noreply@beststore.com',
                [email],
            )
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=True)
        except Exception as e:
            print(f"Email sending error: {str(e)}")

        # Return success response
        return JsonResponse({
            'success': True,
            'message': 'Order placed successfully!',
            'order_number': order.pk,
            'redirect_url': f'/orders/confirmation/{order.pk}/'
        })

    except Exception as e:
        print(f"Order Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Error processing order: {str(e)}'
        }, status=500)


from django.shortcuts import render, get_object_or_404
from .models import Order

def order_confirmation(request, order_id):
    """Display the order confirmation page."""
    order = get_object_or_404(Order, id=order_id)  # Return 404 if the order does not exist
    context = {
        'order': order,
    }
    return render(request, 'orders/confirmation.html', context)

@login_required(login_url='login')
def order_list(request):
    """Display user's orders"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required(login_url='login')
def order_detail(request, order_id):
    """Display order details"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    items = order.items.all()
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': items
    })


@staff_member_required
def paidOrders(request):
    """Staff-only view to list paid orders"""
    qs = Order.objects.filter(status='completed').select_related('user').order_by('-created_at')

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(id__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )

    # Date filtering
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    if date_from:
        try:
            dt = datetime.strptime(date_from, '%Y-%m-%d')
            qs = qs.filter(created_at__date__gte=dt.date())
        except ValueError:
            pass
    if date_to:
        try:
            dt = datetime.strptime(date_to, '%Y-%m-%d')
            qs = qs.filter(created_at__date__lte=dt.date())
        except ValueError:
            pass

    # CSV export
    if request.GET.get('export') == 'csv':
        filename = f"paid_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(resp)
        writer.writerow(['Order ID', 'Customer', 'Email', 'Phone', 'Total', 'Status', 'Created At'])
        for o in qs:
            writer.writerow([
                o.pk,
                f'{o.first_name} {o.last_name}',
                o.email,
                o.phone,
                float(o.total_amount or 0),
                o.status,
                o.created_at.isoformat() if o.created_at else ''
            ])
        return resp

    # Pagination
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 25))
    paginator = Paginator(qs, per_page)
    try:
        paid_orders = paginator.page(page)
    except PageNotAnInteger:
        paid_orders = paginator.page(1)
    except EmptyPage:
        paid_orders = paginator.page(paginator.num_pages)

    context = {
        'paid_orders': paid_orders,
        'q': q,
        'date_from': date_from,
        'date_to': date_to,
        'paginator': paginator,
    }
    return render(request, 'orders/paidOrders.html', context)


def paid_orders_api(request):
    """API endpoint for paid orders"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    qs = Order.objects.filter(status='completed').order_by('-id')
    results = []
    for o in qs:
        results.append({
            'id': o.pk,
            'customer': f'{o.first_name} {o.last_name}',
            'email': o.email,
            'total': float(o.total_amount or 0),
            'currency': 'KES',
            'created_at': o.created_at.isoformat() if o.created_at else '',
        })
    return JsonResponse(results, safe=False)

import random
import string
import base64
import requests
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order
from .generateAcesstoken import get_access_token


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order
from .generateAcesstoken import get_access_token
import base64
from datetime import datetime
import requests

@login_required(login_url='login')
def mpesa_payment(request, order_id):
    """
    Handle M-Pesa payment initiation for orders.
    Generates STK push with custom account reference 'BRAMH' for till identification.
    """
    order = get_object_or_404(Order, id=order_id)  # Fetch the order or return 404 if not found
    payment_response = None

    if request.method == "POST":
        access_token = get_access_token()
        if not access_token:
            payment_response = {'error': 'Access token not found.'}
        else:
            phone_number = request.POST.get('phone_number') or getattr(request.user, 'phone_number', None)
            if not phone_number:
                payment_response = {'error': 'Phone number not provided. Please enter your phone number.'}
            else:
                # Format phone number
                if phone_number.startswith("+"):
                    phone_number = phone_number[1:]
                if phone_number.startswith("0"):
                    phone_number = "254" + phone_number[1:]
                if not phone_number.startswith("254") or len(phone_number) != 12:
                    payment_response = {'error': 'Invalid phone number format. Use 2547XXXXXXXX.'}
                else:
                    # M-Pesa configuration
                    passkey = "46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933"
                    business_short_code = '3581517'
                    till_number = 6391014
                    process_request_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
                    callback_url = 'https://mamamaasaibakers.com/orders/mpesa/callback/'

                    # Timestamp and password
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

                    # Transaction description
                    transaction_desc = f'Payment for Order {order_id}'
                    account_reference = 'BRAMH'

                    # Get amount from the order
                    amount = order.total_amount  # Use the correct field name

                    # STK push headers
                    stk_push_headers = {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + access_token
                    }

                    # STK push payload
                    stk_push_payload = {
                        'BusinessShortCode': business_short_code,
                        'Password': password,
                        'Timestamp': timestamp,
                        'TransactionType': 'CustomerBuyGoodsOnline',
                        'Amount': amount,
                        'PartyA': phone_number,
                        'PartyB': till_number,
                        'PhoneNumber': phone_number,
                        'CallBackURL': callback_url,
                        'AccountReference': account_reference,
                        'TransactionDesc': transaction_desc
                    }

                    # Initiate STK push
                    try:
                        response = requests.post(
                            process_request_url,
                            headers=stk_push_headers,
                            json=stk_push_payload,
                            timeout=30
                        )
                        response.raise_for_status()
                        response_data = response.json()
                        response_code = response_data.get('ResponseCode')

                        if response_code == "0":
                            checkout_request_id = response_data.get('CheckoutRequestID')
                            payment_response = {
                                'success': True,
                                'message': 'STK Push initiated successfully. Please complete payment on your phone.',
                                'CheckoutRequestID': checkout_request_id,
                                'ResponseCode': response_code,
                                'amount': amount,
                                'account_reference': account_reference,
                                'till_number': till_number,
                                'order_number': order_id,
                                'status_url': f'/api/orders/status/{checkout_request_id}/'
                            }
                        else:
                            error_message = response_data.get('errorMessage') or response_data.get('errorDesc') or response_data
                            payment_response = {
                                'error': 'STK Push failed.',
                                'details': error_message,
                                'paybill': business_short_code,
                                'account_reference': account_reference,
                                'till_number': till_number
                            }
                    except requests.exceptions.Timeout:
                        payment_response = {
                            'error': 'Request timeout. Please try again.',
                            'details': 'The payment gateway took too long to respond.',
                            'paybill': business_short_code,
                            'account_reference': account_reference,
                            'till_number': till_number
                        }
                    except requests.exceptions.RequestException as e:
                        payment_response = {
                            'error': 'Failed to initiate STK Push.',
                            'details': str(e),
                            'paybill': business_short_code,
                            'account_reference': account_reference,
                            'till_number': till_number
                        }
                    except Exception as e:
                        payment_response = {
                            'error': 'An unexpected error occurred.',
                            'details': str(e),
                            'paybill': business_short_code,
                            'account_reference': account_reference,
                            'till_number': till_number
                        }

    # Ensure the view always returns an HttpResponse
    context = {
        'order': order,
        'grand_total': order.total_amount,  # Use the correct field name
        'payment_response': payment_response,
    }
    return render(request, 'orders/mpesa_payment.html', context)

# ========================= MPESA CALLBACK HANDLER =========================
@csrf_exempt
def mpesa_callback(request):
    """
    Handle M-Pesa callback notifications.
    Processes successful payments and updates order status.
    Account reference 'BRAMH' identifies payments from the specific till.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            body = data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc', '')
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

            # Initialize variables
            mpesa_receipt = None
            phone_number = None
            amount = None
            account_reference = None

            # ========================= EXTRACT PAYMENT DETAILS =========================
            for item in callback_metadata:
                if item['Name'] == 'MpesaReceiptNumber':
                    mpesa_receipt = item['Value']
                elif item['Name'] == 'PhoneNumber':
                    phone_number = str(item['Value'])
                elif item['Name'] == 'Amount':
                    amount = float(item['Value'])
                elif item['Name'] == 'AccountReference':
                    account_reference = str(item['Value'])

            print(f"Callback received - Receipt: {mpesa_receipt}, Phone: {phone_number}, Amount: {amount}, Account Ref: {account_reference}")

            # ========================= VALIDATE CALLBACK =========================
            if result_code == 0 and mpesa_receipt and account_reference == 'BRAMH':
                try:
                    # Find order by account reference (BRAMH) and phone number
                    order = Order.objects.get(
                        phone=phone_number,
                        is_ordered=False
                    )
                    
                    # ========================= CREATE PAYMENT RECORD =========================
                    payment = Payment.objects.create(
                        user=order.user,
                        payment_id=mpesa_receipt,
                        payment_method="M-Pesa",
                        amount_paid=amount,
                        status="Completed"
                    )
                    
                    # ========================= UPDATE ORDER STATUS =========================
                    order.payment = payment
                    order.is_ordered = True
                    order.status = "Completed"
                    order.save()
                    
                    # ========================= MOVE CART ITEMS TO ORDER PRODUCTS =========================
                    cart_items = CartItem.objects.filter(user=order.user)
                    for item in cart_items:
                        order_product = OrderProduct.objects.create(
                            order=order,
                            payment=payment,
                            user=order.user,
                            product=item.product,
                            quantity=item.quantity,
                            product_price=item.product.price,
                            ordered=True
                        )
                        
                        # Assign product variations
                        order_product.variations.set(item.variations.all())
                        order_product.save()
                        
                        # ========================= REDUCE PRODUCT STOCK =========================
                        product = Product.objects.get(id=item.product.id)
                        product.stock -= item.quantity
                        product.save()
                    
                    # ========================= CLEAR CART =========================
                    cart_items.delete()
                    
                    # ========================= SEND CONFIRMATION EMAIL =========================
                    try:
                        mail_subject = 'Order Confirmation - BestStore'
                        message = render_to_string('orders/order_received_email.html', {
                            'user': order.user,
                            'order': order,
                            'payment': payment,
                        })
                        to_email = order.user.email
                        EmailMessage(
                            mail_subject, 
                            message, 
                            from_email='noreply@beststore.com',
                            to=[to_email]
                        ).send()
                    except Exception as e:
                        print(f"Email sending error: {str(e)}")
                    
                    print(f"Order {order.order_number} confirmed with M-Pesa receipt {mpesa_receipt}")
                    
                    return JsonResponse({
                        "ResultCode": 0, 
                        "ResultDesc": f"Payment received successfully. Till: BRAMH, Receipt: {mpesa_receipt}"
                    })
                
                except Order.DoesNotExist:
                    print(f"Order not found for phone {phone_number}")
                    return JsonResponse({
                        "ResultCode": 1, 
                        "ResultDesc": "Order not found"
                    }, status=404)
                
                except Exception as e:
                    print(f"Error saving payment: {str(e)}")
                    return JsonResponse({
                        "ResultCode": 1, 
                        "ResultDesc": f"Error saving payment: {str(e)}"
                    }, status=500)
            else:
                error_msg = f"Payment not successful or invalid till. Result Code: {result_code}, Account Ref: {account_reference}"
                print(error_msg)
                return JsonResponse({
                    "ResultCode": 1,
                    "ResultDesc": f"Payment not successful: {result_desc}"
                })
        
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return JsonResponse({
                "ResultCode": 1, 
                "ResultDesc": f"Invalid JSON: {str(e)}"
            }, status=400)
        
        except Exception as e:
            print(f"Callback error: {str(e)}")
            return JsonResponse({
                "ResultCode": 1, 
                "ResultDesc": f"Callback error: {str(e)}"
            }, status=400)
    else:
        return HttpResponse("M-Pesa Callback Endpoint", status=200)


def transaction_status_view(request):
    transaction_id = request.GET.get('transaction_id')  # Or get from POST, or hardcode for testing
    result = check_transaction_status(transaction_id)
    return JsonResponse(result)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json





from django.http import JsonResponse
from .account_balance import query_account_balance

def check_account_balance(request):
    result = query_account_balance()
    return JsonResponse(result)

# filepath: c:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE\orders\views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def mpesa_balance_result(request):
    if request.method == "POST":
        # Handle and log the result notification here
        return JsonResponse({"status": "received"})
    return JsonResponse({"error": "Invalid request"}, status=400)

from .transaction_status import check_transaction_status

result = check_transaction_status('TRANSACTION_ID_HERE')
def transaction_status_view(request):
    transaction_id = request.GET.get('transaction_id')  # Or get from POST, or hardcode for testing
    result = check_transaction_status(transaction_id)
    return JsonResponse(result)



# ------------------------------
# Payments View
# ------------------------------
@login_required(login_url='login')
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Save payment details
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    # Update order status
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move cart items to OrderProduct
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order = order
        order_product.payment = payment
        order_product.user = request.user
        order_product.product = item.product
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        # Assign product variations
        order_product.variations.set(item.variations.all())
        order_product.save()

        # Reduce product stock
        product = Product.objects.get(id=item.product.id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    cart_items.delete()

    # Send order confirmation email
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    EmailMessage(mail_subject, message, to=[to_email]).send()

    # Return response
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Transaction

@staff_member_required
def transaction_portal(request):
    transactions = Transaction.objects.all().order_by('-paid_at')
    return render(request, 'orders/transaction_portal.html', {'transactions': transactions})


# ...existing code...
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import csv
from datetime import datetime
from django.http import HttpResponse

@staff_member_required
def paidOrders(request):
    """
    Staff-only view to list paid orders with search, filtering, pagination and CSV export.
    Query params:
      - q: search term (order number, customer name/email, mpesa receipt)
      - from: start date YYYY-MM-DD
      - to: end date YYYY-MM-DD
      - order_by: field to order by (default '-created_at')
      - page: page number
      - per_page: items per page (default 25)
      - export=csv : return CSV of current filtered set
    """
    qs = Order.objects.filter(is_ordered=True).select_related('user', 'payment').order_by('-created_at')

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(order_number__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(payment__payment_id__icontains=q) |
            Q(user__email__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q)
        )

    # Date filtering
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    date_format = '%Y-%m-%d'
    if date_from:
        try:
            dt = datetime.strptime(date_from, date_format)
            qs = qs.filter(created_at__date__gte=dt.date())
        except ValueError:
            pass
    if date_to:
        try:
            dt = datetime.strptime(date_to, date_format)
            qs = qs.filter(created_at__date__lte=dt.date())
        except ValueError:
            pass

    # Ordering
    order_by = request.GET.get('order_by', '-created_at')
    try:
        qs = qs.order_by(order_by)
    except Exception:
        qs = qs.order_by('-created_at')

    # CSV export
    if request.GET.get('export') == 'csv':
        filename = f"paid_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(resp)
        writer.writerow(['Order Number', 'Customer', 'Email', 'Phone', 'Total', 'Payment ID', 'Status', 'Created At'])
        for o in qs:
            customer = (o.user.get_full_name() if getattr(o, 'user', None) else f"{o.first_name or ''} {o.last_name or ''}".strip())
            writer.writerow([
                o.order_number,
                customer,
                o.email or (o.user.email if getattr(o, 'user', None) else ''),
                o.phone or '',
                float(o.order_total or 0),
                (o.payment.payment_id if getattr(o, 'payment', None) else ''),
                getattr(o, 'status', '') or '',
                o.created_at.isoformat() if getattr(o, 'created_at', None) else ''
            ])
        return resp

    # Pagination
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 25))
    paginator = Paginator(qs, per_page)
    try:
        paid_orders = paginator.page(page)
    except PageNotAnInteger:
        paid_orders = paginator.page(1)
    except EmptyPage:
        paid_orders = paginator.page(paginator.num_pages)

    context = {
        'paid_orders': paid_orders,
        'q': q,
        'date_from': date_from,
        'date_to': date_to,
        'order_by': order_by,
        'paginator': paginator,
    }
    return render(request, 'orders/paidOrders.html', context)
# ...existing code...


# ...existing code...
from django.http import JsonResponse
from django.utils import timezone
from .models import Order

def paid_orders_api(request):
    """
    GET /api/orders?status=paid
    Returns a JSON array of paid orders. Public GET (adjust auth as needed).
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    status = request.GET.get('status', '').lower()
    # only return paid when status=paid requested
    if status != 'paid':
        return JsonResponse({'error': 'Specify ?status=paid to get paid orders'}, status=400)

    qs = Order.objects.filter(is_ordered=True).order_by('-id')  # adjust filter if you use order.status or payment.status
    results = []
    for o in qs:
        paid_at = None
        if hasattr(o, 'created_at') and o.created_at:
            paid_at = o.created_at.isoformat()
        elif hasattr(o, 'updated_at') and o.updated_at:
            paid_at = o.updated_at.isoformat()
        results.append({
            'id': o.order_number,
            'customer': {
                'name': (o.user.get_full_name() if getattr(o, 'user', None) and hasattr(o.user, 'get_full_name') else (
                         (o.first_name or '') + ' ' + (o.last_name or '')
                ).strip()) if (getattr(o, 'user', None) or getattr(o, 'first_name', None)) else '',
                'email': getattr(o, 'email', '') or (getattr(o.user, 'email', '') if getattr(o, 'user', None) else '')
            },
            'total': float(o.order_total or 0),
            'currency': 'KES',
            'paidAt': paid_at,
            'viewUrl': f'/orders/{o.order_number}/',
            'receiptUrl': (o.payment.payment_id if getattr(o, 'payment', None) else None),
        })
    return JsonResponse(results, safe=False)


from django.http import HttpResponse

def mpesa_transaction_result(request):
    return HttpResponse("OK", status=200)