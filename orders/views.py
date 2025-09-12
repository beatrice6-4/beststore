from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json

from store.models import Product
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage

from django.template.loader import render_to_string

@login_required(login_url='login')
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
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
            data.save()
            # Generate order number
            current_date = datetime.now().strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

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
        return redirect('checkout')
@login_required(login_url='login')
def mpesa_payment(request, order_number):
    current_user = request.user
    order = Order.objects.get(user=current_user, order_number=order_number, is_ordered=False)
    cart_items = CartItem.objects.filter(user=current_user)

    total = 0
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'orders/mpesa_payment.html', context)

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, user=request.user, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    



# Mpesa Integrationimport requests
import base64
from datetime import datetime
from django.conf import settings

def lipa_na_mpesa_online(phone, amount, order_number):
    """
    Initiates an Mpesa STK Push request.
    Returns the API response as a dict.
    """
    # Ensure phone is in 2547XXXXXXXX format
    if phone.startswith('07'):
        phone = '254' + phone[1:]
    elif phone.startswith('+254'):
        phone = phone[1:]
    elif not phone.startswith('254'):
        raise ValueError("Phone number must start with 254")

    # Ensure amount is an integer
    try:
        amount = int(float(amount))
    except Exception:
        raise ValueError("Invalid amount")

    # Get access token
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    access_token = r.json().get('access_token')

    # Prepare STK Push request
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode('utf-8')
    ).decode('utf-8')
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,  # Set this in your settings.py
        "AccountReference": str(order_number),
        "TransactionDesc": "Order Payment"
    }

    stk_push_url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    response = requests.post(stk_push_url, json=payload, headers=headers)
    return response.json()


from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def mpesa_callback(request):
    """
    Handles the Mpesa STK Push callback.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        print("Mpesa Callback data:", data)  # Log the callback data for debugging

        # Extract relevant information from the callback data
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        result_desc = data.get('Body', {}).get('stkCallback', {}).get('ResultDesc')
        merchant_request_id = data.get('Body', {}).get('stkCallback', {}).get('MerchantRequestID')
        checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        amount = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])[0].get('Value') if result_code == 0 else 0
        mpesa_receipt_number = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])[1].get('Value') if result_code == 0 else ''
        phone_number = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])[3].get('Value') if result_code == 0 else ''
        transaction_date = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])[4].get('Value') if result_code == 0 else ''

        # Here you would typically update your Order and Payment models based on the callback data
        # For example, find the order by MerchantRequestID or CheckoutRequestID and mark it as paid

        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
    else:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid request method'})
    
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def mpesa_validation(request):
    """
    Handles the Mpesa C2B validation request.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        print("Mpesa Validation data:", data)  # Log the validation data for debugging

        # Here you would typically validate the transaction details
        # For example, check if the account number exists in your system

        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
    else:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid request method'})


    