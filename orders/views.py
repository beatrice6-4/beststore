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

            # Redirect to payment page
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
        else:
            return render(request, 'orders/checkout.html', {'form': form, 'cart_items': cart_items})
    else:
        return redirect('checkout')
    





# Example in views.py
from django.shortcuts import redirect

def placeOrder(request):
    if request.method == "POST":
        # ...process order...
        # Assume you create an order object and get its order_number
        order = Order.objects.create(...)  # your order creation logic
        return redirect('mpesa_payment', order_number=order.order_number)
    # ...existing GET logic...






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



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Order
from .generateAcesstoken import get_access_token
import base64
import requests
from datetime import datetime

import requests
from datetime import datetime
import json
import base64
from django.http import JsonResponse

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .generateAcesstoken import get_access_token
import base64
import requests
from datetime import datetime

@csrf_exempt
def initiate_stk_push_sandbox(request):
    if request.method == "POST":
        access_token = get_access_token()
        if not access_token:
            return JsonResponse({'error': 'Access token not found.'})

        phone_number = request.POST.get('phone_number')
        if not phone_number:
            return JsonResponse({'error': 'Phone number not provided.'})

        # Format phone number for sandbox (must be 2547XXXXXXXX)
        if phone_number.startswith("+"):
            phone_number = phone_number[1:]
        if phone_number.startswith("0"):
            phone_number = "254" + phone_number[1:]
        if not phone_number.startswith("254") or len(phone_number) != 12:
            return JsonResponse({'error': 'Invalid phone number format. Use 2547XXXXXXXX.'})

        # Sandbox credentials
        business_short_code = '174379'
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        callback_url = 'https://mamamaasaibakers.com/orders/mpesa/callback/'  # Use your test callback URL

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
        amount = 1  # Sandbox only allows 1 Ksh
        account_reference = 'BESTSTORE'
        transaction_desc = 'Sandbox STK Push Test'

        stk_push_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }

        stk_push_payload = {
            'BusinessShortCode': business_short_code,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': phone_number,
            'PartyB': business_short_code,
            'PhoneNumber': phone_number,
            'CallBackURL': callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }

        try:
            response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
            response.raise_for_status()
            response_data = response.json()
            response_code = response_data.get('ResponseCode')
            if response_code == "0":
                return JsonResponse({
                    'message': 'Sandbox STK Push initiated successfully. Check your test phone for the prompt.',
                    'CheckoutRequestID': response_data.get('CheckoutRequestID'),
                    'ResponseCode': response_code
                })
            else:
                error_message = response_data.get('errorMessage') or response_data.get('errorDesc') or response_data
                return JsonResponse({'error': 'STK Push failed.', 'details': error_message})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'Failed to initiate STK Push.', 'details': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request method. Use POST.'})


from django.shortcuts import render
from .stkPush import initiate_stk_push
from .query import query_stk_status


# ------------------------------
# Mpesa Callback View
# ------------------------------
@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            body = data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

            if result_code == 0:
                # Extract payment details
                mpesa_receipt = None
                phone_number = None
                amount = None
                order_number = None

                for item in callback_metadata:
                    if item['Name'] == 'MpesaReceiptNumber':
                        mpesa_receipt = item['Value']
                    elif item['Name'] == 'PhoneNumber':
                        phone_number = str(item['Value'])
                    elif item['Name'] == 'Amount':
                        amount = float(item['Value'])
                    elif item['Name'] == 'AccountReference':
                        order_number = str(item['Value'])

                # Update order and payment
                order = Order.objects.get(order_number=order_number, phone=phone_number, is_ordered=False)
                payment = Payment.objects.create(
                    user=order.user,
                    payment_id=mpesa_receipt,
                    payment_method="Mpesa",
                    amount_paid=amount,
                    status="Completed"
                )
                order.payment = payment
                order.is_ordered = True
                order.status = "Completed"
                order.save()

                return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
            else:
                return JsonResponse({"ResultCode": 1, "ResultDesc": "Payment not successful"})
        except Exception as e:
            return JsonResponse({"ResultCode": 1, "ResultDesc": str(e)}, status=400)
    else:
        return HttpResponse("Mpesa callback endpoint.", status=200)

# ------------------------------
# Order Complete View
# ------------------------------
@login_required(login_url='login')
def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, user=request.user, is_ordered=True)
        payment = Payment.objects.get(payment_id=payment_id, user=request.user)
        ordered_products = OrderProduct.objects.filter(order=order)

        subtotal = sum([item.product_price * item.quantity for item in ordered_products])

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')
    



from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def transactions(request):
    # Example: Fetch all transactions for the logged-in user
    user_transactions = Payment.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'transactions': user_transactions,
    }
    return render(request, 'orders/transactions.html', context)