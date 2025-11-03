import requests
from datetime import datetime
import json
import base64
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .generateAcesstoken import get_access_token
from .models import Order, Payment
from accounts.models import Account

@csrf_exempt
def initiate_stk_push(request, order_number):
    """
    Initiates an STK Push request to Safaricom's M-Pesa API for payment.
    """
    # Step 1: Get access token
    access_token = get_access_token()
    if not access_token:
        return JsonResponse({'error': 'Access token not found.'})


    # Step 2: Fetch order details
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        amount = int(order.order_total)  # Ensure the amount is an integer
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found.'})

    # Step 3: Prepare STK Push parameters
    passkey = "46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933"  # Replace with your actual passkey
    business_short_code = '3581517'
    process_request_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    callback_url = 'https://mamamaasaibakers.com/orders/mpesa/callback/'  # Replace with your actual callback URL
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
    transaction_desc = f'Payment for Order {order_number}'
    account_reference = f'Order-{order_number}'

    # Format the phone number to ensure it is in the correct format (2547XXXXXXXX)
    phone_number = request.user.phone_number
    if phone_number.startswith("0"):
        phone_number = "254" + phone_number[1:]

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
        'PartyA': phone_number,  # The user's phone number
        'PartyB': business_short_code,  # The PayBill number
        'PhoneNumber': phone_number,  # The user's phone number
        'CallBackURL': callback_url,
        'AccountReference': account_reference,
        'TransactionDesc': transaction_desc
    }

    # Step 4: Send STK Push request
    try:
        print("STK Push Payload:", stk_push_payload)  # Log the payload
        print("STK Push Headers:", stk_push_headers)  # Log the headers
        response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
        response.raise_for_status()
        response_data = response.json()
        print("STK Push Response:", response_data)  # Log the response

        # Check the response for success
        response_code = response_data.get('ResponseCode')
        if response_code == "0":
            checkout_request_id = response_data.get('CheckoutRequestID')
            return JsonResponse({
                'message': 'STK Push initiated successfully.',
                'CheckoutRequestID': checkout_request_id,
                'ResponseCode': response_code,
                'amount': amount
            })
        else:
            return JsonResponse({
                'error': 'STK Push failed.',
                'details': response_data
            })
    except requests.exceptions.RequestException as e:
        print("STK Push Error:", str(e))  # Log the error for debugging
        return JsonResponse({'error': 'Failed to initiate STK Push. Please try again.'})

@csrf_exempt
def mpesa_callback(request):
    """
    Handles the callback from Safaricom's M-Pesa API after an STK Push request.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("M-Pesa Callback Data:", data)  # Log the callback data for debugging
            body = data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

            if result_code == 0:
                # Extract metadata
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

                if not all([mpesa_receipt, phone_number, amount, account_reference]):
                    return JsonResponse({"ResultCode": 1, "ResultDesc": "Incomplete callback data"}, status=400)

                # Update order and payment details
                try:
                    order = Order.objects.get(order_number=account_reference, is_ordered=False)
                except Order.DoesNotExist:
                    return JsonResponse({"ResultCode": 1, "ResultDesc": "Order not found"}, status=404)

                user = Account.objects.get(id=order.user.id)
                payment = Payment.objects.create(
                    user=user,
                    payment_id=mpesa_receipt,
                    payment_method="Mpesa",
                    amount_paid=amount,
                    status="Completed"
                )

                order.payment = payment
                order.is_ordered = True
                order.status = "Completed"
                order.save()

                return JsonResponse({"ResultCode": 0, "ResultDesc": "Payment processed successfully."})

            return JsonResponse({"ResultCode": 1, "ResultDesc": "Payment not successful."})

        except Exception as e:
            print("M-Pesa Callback Error:", str(e))  # Log the error for debugging
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Failed to process callback."}, status=400)
    else:
        return HttpResponse("M-Pesa callback endpoint.", status=200)