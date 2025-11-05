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
                # Format phone number
                original_phone = phone_number
                if phone_number.startswith("+"):
                    phone_number = phone_number[1:]
                if phone_number.startswith("0"):
                    phone_number = "254" + phone_number[1:]
                if not phone_number.startswith("254") or len(phone_number) != 12:
                    payment_response = {'error': f'Invalid phone number format ({original_phone}). Use 2547XXXXXXXX.'}
                else:
                    passkey = "46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933"  # LIVE passkey
                    business_short_code = '3581517'  # LIVE shortcode
                    process_request_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
                    callback_url = 'https://mamamaasaibakers-917922e1976b.herokuapp.com/orders/mpesa/callback/'
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
                    transaction_desc = f'Payment for Order {order_number}'

                    # Generate AccountReference: 3 random capital letters + 3 random digits
                    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))
                    random_digits = ''.join(random.choices(string.digits, k=3))
                    account_reference = f'{random_letters}{random_digits}'

                    amount = int(order.order_total)

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

                    paybill_instructions = (
                        f"If you do not receive the STK Push on your phone, "
                        f"you can pay directly via M-Pesa Paybill {business_short_code} "
                        f"and use Account Number {account_reference}."
                    )

                    try:
                        response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                        print("STK Push API Response:", response.text)  # For debugging
                        # Optionally, log to a file for persistent debugging:
                        with open('stkpush_debug.log', 'a') as log_file:
                            log_file.write(f"{datetime.now()} - Payload: {stk_push_payload}\nResponse: {response.text}\n\n")
                        response.raise_for_status()
                        response_data = response.json()
                        response_code = response_data.get('ResponseCode')
                        if response_code == "0":
                            checkout_request_id = response_data.get('CheckoutRequestID')
                            payment_response = {
                                'message': 'STK Push initiated successfully. Please complete payment on your phone by entering your M-Pesa PIN.',
                                'CheckoutRequestID': checkout_request_id,
                                'ResponseCode': response_code,
                                'amount': amount,
                                'paybill': business_short_code,
                                'account_reference': account_reference,
                                'paybill_instructions': paybill_instructions
                            }
                        else:
                            error_message = response_data.get('errorMessage') or response_data.get('errorDesc') or response_data
                            payment_response = {
                                'error': 'STK Push failed.',
                                'details': error_message,
                                'api_response': response.text,  # Show full API response for debugging
                                'paybill': business_short_code,
                                'account_reference': account_reference,
                                'paybill_instructions': paybill_instructions
                            }
                    except requests.exceptions.RequestException as e:
                        payment_response = {
                            'error': 'Failed to initiate STK Push.',
                            'details': str(e),
                            'paybill': business_short_code,
                            'account_reference': account_reference,
                            'paybill_instructions': paybill_instructions
                        }

    context = {
        'order': order,
        'grand_total': order.order_total,
        'payment_response': payment_response,
    }
    return render(request, 'orders/mpesa_payment.html', context)


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