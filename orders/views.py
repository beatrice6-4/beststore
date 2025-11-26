from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Order, Payment, OrderProduct
from carts.models import CartItem
from store.models import Product
from accounts.models import Account
from .forms import OrderForm
from .generateAcesstoken import get_access_token
from .query import query_stk_status
from datetime import datetime
import json

# ------------------------------
# Place Order View
# ------------------------------
@login_required(login_url='login')
def placeOrder(request, total=0, quantity=0):
    current_user = request.user

    # Check if the cart is empty
    cart_items = CartItem.objects.filter(user=current_user)
    if not cart_items.exists():
        return redirect('store')

    # Calculate total, tax, and grand total
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Save billing information to the Order model
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.is_ordered = False
            data.save()

            # Generate order number
            current_date = datetime.now().strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # Redirect to mpesa payment page
            return redirect('mpesa_payment', order_number=order_number)
        else:
            return render(request, 'orders/payments.html', {'form': form, 'cart_items': cart_items})
    else:
        return redirect('checkout')




import random
import string
import base64
import requests
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order
from .generateAcesstoken import get_access_token

@login_required(login_url='login')
def mpesa_payment(request, order_number):
    """
    Handle M-Pesa payment initiation for orders.
    Generates STK push with custom account reference 'BRAMH' for till identification.
    """
    order = get_object_or_404(Order, order_number=order_number, user=request.user, is_ordered=False)
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
                # ========================= PHONE NUMBER FORMATTING =========================
                if phone_number.startswith("+"):
                    phone_number = phone_number[1:]
                if phone_number.startswith("0"):
                    phone_number = "254" + phone_number[1:]
                if not phone_number.startswith("254") or len(phone_number) != 12:
                    payment_response = {'error': 'Invalid phone number format. Use 2547XXXXXXXX.'}
                else:
                    # ========================= M-PESA CONFIGURATION =========================
                    passkey = "46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933"  # LIVE passkey for 3581517
                    business_short_code = '3581517'  # LIVE Paybill shortcode
                    till_number = 6391014  # Till number (PartyB)
                    process_request_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
                    callback_url = 'https://mamamaasaibakers.com/orders/mpesa/callback/'
                    
                    # ========================= TIMESTAMP & PASSWORD =========================
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
                    
                    # ========================= TRANSACTION DESCRIPTION =========================
                    transaction_desc = f'Payment for Order {order_number}'
                    
                    # ========================= CUSTOM ACCOUNT REFERENCE (BRAMH) =========================
                    # Use fixed account reference 'BRAMH' for till identification
                    account_reference = 'BRAMH'
                    
                    # ========================= GET AMOUNT FROM FORM =========================
                    amount = request.POST.get('amount')
                    try:
                        amount = int(amount)
                        if amount <= 0:
                            payment_response = {'error': 'Amount must be greater than 0.'}
                            context = {
                                'order': order,
                                'grand_total': order.order_total,
                                'payment_response': payment_response,
                            }
                            return render(request, 'orders/mpesa_payment.html', context)
                    except (TypeError, ValueError):
                        payment_response = {'error': 'Invalid amount entered.'}
                        context = {
                            'order': order,
                            'grand_total': order.order_total,
                            'payment_response': payment_response,
                        }
                        return render(request, 'orders/mpesa_payment.html', context)

                    # ========================= STK PUSH HEADERS =========================
                    stk_push_headers = {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + access_token
                    }

                    # ========================= STK PUSH PAYLOAD =========================
                    stk_push_payload = {
                        'BusinessShortCode': business_short_code,
                        'Password': password,
                        'Timestamp': timestamp,
                        'TransactionType': 'CustomerBuyGoodsOnline',
                        'Amount': amount,
                        'PartyA': phone_number,
                        'PartyB': till_number,  # Till number
                        'PhoneNumber': phone_number,
                        'CallBackURL': callback_url,
                        'AccountReference': account_reference,  # BRAMH
                        'TransactionDesc': transaction_desc
                    }

                    # ========================= INITIATE STK PUSH =========================
                    try:
                        response = requests.post(
                            process_request_url, 
                            headers=stk_push_headers, 
                            json=stk_push_payload,
                            timeout=30
                        )
                        print("STK Push API Response:", response.text)
                        response.raise_for_status()
                        response_data = response.json()
                        response_code = response_data.get('ResponseCode')
                        
                        if response_code == "0":
                            checkout_request_id = response_data.get('CheckoutRequestID')
                            payment_response = {
                                'success': True,
                                'message': f'STK Push initiated successfully. Please complete payment on your phone by entering your M-Pesa PIN. Payment goes to BRAMH till.',
                                'CheckoutRequestID': checkout_request_id,
                                'ResponseCode': response_code,
                                'amount': amount,
                                'account_reference': account_reference,
                                'till_number': till_number,
                                'order_number': order_number,
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

    context = {
        'order': order,
        'grand_total': order.order_total,
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

@csrf_exempt
def mpesa_transaction_result(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            # Log the result for debugging
            print("M-Pesa Transaction Result:", data)
            # Optionally, save the result to your database here

            # You can extract and process fields as needed, for example:
            result_code = data.get('Result', {}).get('ResultCode')
            result_desc = data.get('Result', {}).get('ResultDesc')
            transaction_id = data.get('Result', {}).get('TransactionID')
            conversation_id = data.get('Result', {}).get('ConversationID')

            # Respond to Safaricom
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Received successfully"})
        except Exception as e:
            print("Error processing M-Pesa transaction result:", str(e))
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Error processing result"}, status=400)
    else:
        return HttpResponse("M-Pesa Transaction Result Endpoint", content_type="text/plain")






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