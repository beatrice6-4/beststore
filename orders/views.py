from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
import json
import datetime
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

@login_required(login_url='login')
def placeOrder(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

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
            # Generate order number using correct datetime usage
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
            context = {
                'form': form,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/checkout.html', context)
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


@login_required(login_url='login')
def payment_success(request, order_number):
    """
    Call this view after a successful payment.
    It records payment details and marks the order as paid.
    """
    # Example: get payment details from request or payment gateway callback
    payment_id = request.GET.get('payment_id')  # or from POST/callback
    payment_method = request.GET.get('payment_method', 'Mpesa')
    amount_paid = request.GET.get('amount_paid')  # or from order/order_total
    status = request.GET.get('status', 'Paid to Account')

    try:
        order = Order.objects.get(order_number=order_number, user=request.user, is_ordered=False)
    except Order.DoesNotExist:
        return HttpResponse("Order not found.", status=404)

    # Create Payment record
    payment = Payment.objects.create(
        user=request.user,
        payment_id=payment_id,
        payment_method=payment_method,
        amount_paid=amount_paid or order.order_total,
        status=status
    )

    # Link payment to order and mark as ordered
    order.payment = payment
    order.is_ordered = True
    order.status = "Completed"
    order.save()

    # Optionally, update OrderProduct records
    order_products = OrderProduct.objects.filter(order=order)
    for op in order_products:
        op.payment = payment
        op.ordered = True
        op.save()

    # Show a success page or redirect
    return render(request, 'orders/payment_success.html', {'order': order, 'payment': payment})





import requests
from datetime import datetime
import json
import base64
from django.http import JsonResponse
from .generateAcesstoken import get_access_token

def initiate_stk_push(request):
    access_token_response = get_access_token(request)
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if access_token:
            if request.method == "POST":
                phone = request.POST.get("phone")  # Get phone from form
            else:
                phone = None
            passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
            business_short_code = '174379'
            process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            callback_url = 'https://mamamaasaibakers.com/orders/mpesa/callback/'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
            party_a = phone
            party_b = business_short_code
            account_reference = '5429863'
            transaction_desc = 'Payment of order - MAMAMAASAIBAKES'
            amount = 1  # Set a default amount or retrieve from order
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
                'PartyA': party_a,
                'PartyB': business_short_code,
                'PhoneNumber': party_a,
                'CallBackURL': callback_url,
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }

            try:
                response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                response.raise_for_status()   
                response_data = response.json()
                checkout_request_id = response_data['CheckoutRequestID']
                response_code = response_data['ResponseCode']
                
                if response_code == "0":
                    return JsonResponse({'CheckoutRequestID': checkout_request_id, 'ResponseCode': response_code})
                else:
                    return JsonResponse({'error': 'STK push failed.'})
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'error': 'Access token not found.'})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})
    
from .query import query_stk_status

def check_stk_status(request, order_number):
    response = query_stk_status(order_number)
    return JsonResponse(response)



from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, Payment, OrderProduct
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def order_complete(request):
    """
    Displays the order completion summary after successful payment.
    Expects 'order_number' and 'payment_id' as GET parameters.
    """
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, user=request.user, is_ordered=False)
        payment = Payment.objects.get(payment_id=payment_id, user=request.user)
        ordered_products = OrderProduct.objects.filter(order=order)

        subtotal = sum([op.product_price * op.quantity for op in ordered_products])

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

from .generateAcesstoken import get_access_token
from .stkPush import initiate_stk_push
from .query import query_stk_status



def payment(request, order_number):
    order = Order.objects.get(order_number=order_number, user=request.user)
    amount = int(order.order_total)
    context = {
        'order': order,
        'amount': amount,
    }
    return render(request, 'orders/payments.html', context)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json

from .models import Order, Payment, OrderProduct
from carts.models import CartItem

@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            # Extract relevant info from the callback
            body = data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

            if result_code == 0:
                # Extract details
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

                # Find the order (adjust filter as needed)
                try:
                    order = Order.objects.get(order_number=order_number, phone=phone_number, is_ordered=False)
                except Order.DoesNotExist:
                    return JsonResponse({"ResultCode": 1, "ResultDesc": "Order not found"}, status=404)

                # Create Payment record
                payment = Payment.objects.create(
                    user=order.user,
                    payment_id=mpesa_receipt,
                    payment_method="Mpesa",
                    amount_paid=amount,
                    status="Completed"
                )

                # Link payment to order and mark as ordered
                order.payment = payment
                order.is_ordered = True
                order.status = "Completed"
                order.save()

                # Move cart items to OrderProduct
                cart_items = CartItem.objects.filter(user=order.user)
                for item in cart_items:
                    orderproduct = OrderProduct.objects.create(
                        order=order,
                        payment=payment,
                        user=order.user,
                        product=item.product,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        ordered=True
                    )
                    orderproduct.variations.set(item.variations.all())
                    orderproduct.save()

                    # Reduce product stock
                    product = item.product
                    product.stock -= item.quantity
                    product.save()

                # Clear cart
                cart_items.delete()

                return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

            # If payment failed
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Payment not successful"})

        except Exception as e:
            print("Mpesa Callback Error:", str(e))
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Failed"}, status=400)
    else:
        return HttpResponse("Mpesa callback endpoint.", status=200)
    



from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Order, Payment
from accounts.models import Account

@login_required(login_url='login')
def payments(request, order_number):
    """
    Handles payment for an order and records the transaction.
    """
    order = get_object_or_404(Order, order_number=order_number, user=request.user, is_ordered=False)
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = order.order_total

        # Here you would call your STK Push function and handle response.
        # For demonstration, let's assume payment is successful and record it.

        payment = Payment.objects.create(
            user=request.user,
            payment_id="MPESA123456",  # This should be the actual payment ID from Mpesa
            payment_method="Mpesa",
            amount_paid=amount,
            status="Completed"
        )
        order.payment = payment
        order.is_ordered = True
        order.status = "Completed"
        order.save()

        return redirect('order_complete', order_number=order.order_number)

    context = {
        'order': order,
    }
    return render(request, 'orders/payments.html', context)

@login_required(login_url='login')
def transactions(request):
    """
    Lists all payments made by the logged-in user.
    """
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'payments': payments,
    }
    return render(request, 'orders/transactions.html', context)

@csrf_exempt
def mpesa_callback(request):
    """
    Receives Mpesa callback and records the transaction.
    """
    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body.decode('utf-8'))
            body = data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

            if result_code == 0:
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

                try:
                    order = Order.objects.get(order_number=order_number, phone=phone_number, is_ordered=False)
                except Order.DoesNotExist:
                    return JsonResponse({"ResultCode": 1, "ResultDesc": "Order not found"}, status=404)

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

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Payment not successful"})

        except Exception as e:
            print("Mpesa Callback Error:", str(e))
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Failed"}, status=400)
    else:
        return HttpResponse("Mpesa callback endpoint.", status=200)