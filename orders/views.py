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
from .models import Order, OrderItem, Transaction
from datetime import datetime
import json
import csv
import base64
import requests


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
                'items': order.order_products.all()
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


def order_confirmation(request, order_id):
    """Display the order confirmation page."""
    order = get_object_or_404(Order, id=order_id)
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
    items = order.order_products.all()
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': items
    })


# ========================= MPESA PAYMENT VIEW =========================
from .generateAcesstoken import get_access_token

@login_required(login_url='login')
def mpesa_payment(request, order_id):
    """
    Handle M-Pesa payment initiation for orders.
    Generates STK push with custom account reference 'BRAMH' for till identification.
    """
    order = get_object_or_404(Order, id=order_id)
    payment_response = None

    if request.method == "POST":
        try:
            access_token = get_access_token()
            if not access_token:
                payment_response = {
                    'error': 'Failed to get access token',
                    'details': 'Unable to connect to M-Pesa gateway. Please try again.'
                }
            else:
                phone_number = request.POST.get('phone_number', '').strip()
                
                if not phone_number:
                    payment_response = {
                        'error': 'Phone number is required',
                        'details': 'Please enter your M-Pesa registered phone number.'
                    }
                else:
                    # ========================= PHONE NUMBER FORMATTING =========================
                    # Remove any spaces, dashes, or special characters
                    phone_number = ''.join(filter(str.isdigit, phone_number))
                    
                    # Convert to international format (254XXXXXXXXX)
                    if phone_number.startswith("+"):
                        phone_number = phone_number[1:]
                    if phone_number.startswith("0"):
                        phone_number = "254" + phone_number[1:]
                    if not phone_number.startswith("254"):
                        phone_number = "254" + phone_number
                    
                    # Validate phone number format
                    if len(phone_number) != 12 or not phone_number.startswith("254"):
                        payment_response = {
                            'error': 'Invalid phone number format',
                            'details': 'Please enter a valid phone number (e.g., 254712345678 or 0712345678).'
                        }
                    else:
                        # ========================= M-PESA CONFIGURATION =========================
                        passkey = "46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933"
                        business_short_code = '3581517'
                        till_number = 6391014
                        process_request_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
                        callback_url = 'https://mamamaasaibakers.com/orders/mpesa/callback/'

                        # Generate timestamp and password
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        password_string = business_short_code + passkey + timestamp
                        password = base64.b64encode(password_string.encode()).decode()

                        # Transaction details
                        transaction_desc = f'Payment for Order #{order_id}'
                        account_reference = 'BRAMH'
                        amount = int(order.total_amount)

                        # STK Push Headers
                        stk_push_headers = {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + access_token
                        }

                        # STK Push Payload
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

                        print(f"Initiating STK Push: {stk_push_payload}")

                        # ========================= INITIATE STK PUSH =========================
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

                            print(f"STK Push Response: {response_data}")

                            if response_code == "0":
                                checkout_request_id = response_data.get('CheckoutRequestID')
                                
                                # Save transaction record
                                Transaction.objects.create(
                                    order=order,
                                    mpesa_request_id=checkout_request_id,
                                    phone_number=phone_number,
                                    amount=amount,
                                    status='initiated',
                                    response_code=response_code
                                )
                                
                                payment_response = {
                                    'success': True,
                                    'message': 'STK Push sent successfully! Check your phone for a payment prompt.',
                                    'CheckoutRequestID': checkout_request_id,
                                    'ResponseCode': response_code,
                                    'amount': amount,
                                    'account_reference': account_reference,
                                    'till_number': till_number,
                                    'order_number': order_id,
                                    'phone_number': phone_number
                                }
                            else:
                                error_message = response_data.get('errorMessage', 'Unknown error')
                                payment_response = {
                                    'error': 'STK Push Failed',
                                    'details': error_message,
                                    'response_code': response_code
                                }

                        except requests.exceptions.Timeout:
                            payment_response = {
                                'error': 'Request Timeout',
                                'details': 'The M-Pesa gateway took too long to respond. Please try again.'
                            }
                        except requests.exceptions.RequestException as e:
                            payment_response = {
                                'error': 'Network Error',
                                'details': str(e)
                            }
                        except Exception as e:
                            payment_response = {
                                'error': 'Unexpected Error',
                                'details': str(e)
                            }
                            print(f"STK Push Error: {str(e)}")

        except Exception as e:
            payment_response = {
                'error': 'Error Processing Request',
                'details': str(e)
            }
            print(f"Payment Error: {str(e)}")

    context = {
        'order': order,
        'grand_total': order.total_amount,
        'payment_response': payment_response,
    }
    return render(request, 'orders/mpesa_payment.html', context)


# ========================= MPESA CALLBACK HANDLER =========================
@csrf_exempt
def mpesa_callback(request):
    """
    Handle M-Pesa callback notifications.
    Processes successful payments and updates order status.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            body = data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc', '')
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

            # Extract payment details
            mpesa_receipt = None
            phone_number = None
            amount = None
            account_reference = None

            for item in callback_metadata:
                if item['Name'] == 'MpesaReceiptNumber':
                    mpesa_receipt = item['Value']
                elif item['Name'] == 'PhoneNumber':
                    phone_number = str(item['Value'])
                elif item['Name'] == 'Amount':
                    amount = float(item['Value'])
                elif item['Name'] == 'AccountReference':
                    account_reference = str(item['Value'])

            print(f"Callback - Receipt: {mpesa_receipt}, Phone: {phone_number}, Amount: {amount}, Ref: {account_reference}")

            # Validate callback
            if result_code == 0 and mpesa_receipt and account_reference == 'BRAMH':
                try:
                    # Find order and update status
                    order = Order.objects.get(phone__icontains=phone_number[-9:])
                    
                    # Update order status to completed
                    order.status = 'completed'
                    order.save()
                    
                    # Update or create transaction record
                    Transaction.objects.filter(order=order).update(
                        mpesa_receipt=mpesa_receipt,
                        amount=amount,
                        status='completed',
                        paid_at=datetime.now()
                    )

                    print(f"Order {order.id} payment completed with receipt {mpesa_receipt}")

                    return JsonResponse({
                        "ResultCode": 0,
                        "ResultDesc": "Payment received successfully"
                    })

                except Order.DoesNotExist:
                    print(f"Order not found for phone {phone_number}")
                    return JsonResponse({
                        "ResultCode": 1,
                        "ResultDesc": "Order not found"
                    }, status=404)

                except Exception as e:
                    print(f"Error processing callback: {str(e)}")
                    return JsonResponse({
                        "ResultCode": 1,
                        "ResultDesc": f"Error: {str(e)}"
                    }, status=500)
            else:
                print(f"Invalid callback - Code: {result_code}, Desc: {result_desc}")
                return JsonResponse({
                    "ResultCode": 1,
                    "ResultDesc": f"Payment unsuccessful: {result_desc}"
                })

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return JsonResponse({
                "ResultCode": 1,
                "ResultDesc": f"Invalid JSON"
            }, status=400)

        except Exception as e:
            print(f"Callback error: {str(e)}")
            return JsonResponse({
                "ResultCode": 1,
                "ResultDesc": f"Error: {str(e)}"
            }, status=400)
    else:
        return HttpResponse("M-Pesa Callback Endpoint", status=200)


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


@staff_member_required
def transaction_portal(request):
    """Staff-only transaction monitoring portal"""
    transactions = Transaction.objects.all().order_by('-created_at')
    return render(request, 'orders/transaction_portal.html', {'transactions': transactions})


def mpesa_transaction_result(request):
    """M-Pesa transaction result endpoint"""
    return HttpResponse("OK", status=200)