import requests
from datetime import datetime
import json
import base64
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .generateAcesstoken import get_access_token
from .models import Order, Payment
from accounts.models import Account

@csrf_exempt
def initiate_stk_push(request, order_number):
    # Get access token for sandbox environment
    access_token_response = get_access_token(request)
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if not access_token:
            return JsonResponse({'error': 'Access token not found.'})

        # Fetch the exact amount from the order
        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
            amount = int(order.order_total)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found.'})

        # Get phone number from form
        if request.method == "POST":
            phone = request.POST.get("phone")
            if not phone:
                return JsonResponse({'error': 'Phone number is required.'})
        else:
            return JsonResponse({'error': 'Invalid request method.'})

        # Prepare STK Push parameters for sandbox payments
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        business_short_code = '600986'
        process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl'
        callback_url = 'https://your-dev-callback-url.com/orders/mpesa/callback/'  # Use a test callback URL
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
        account_reference = 'MAMAMAASAI BAKERS'
        transaction_desc = f'Payment of order {order_number} - MAMAMAASAI BAKERS'

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
            'PartyA': phone,
            'PartyB': business_short_code,
            'PhoneNumber': phone,
            'CallBackURL': callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc 
        }

        try:
            response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
            response.raise_for_status()
            response_data = response.json()
            checkout_request_id = response_data.get('CheckoutRequestID')
            response_code = response_data.get('ResponseCode')

            if response_code == "0":
                return JsonResponse({'CheckoutRequestID': checkout_request_id, 'ResponseCode': response_code, 'amount': amount})
            else:
                return JsonResponse({'error': 'STK push failed.', 'details': response_data})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})

@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
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
                if not all([mpesa_receipt, phone_number, amount, order_number]):
                    return JsonResponse({"ResultCode": 1, "ResultDesc": "Incomplete callback data"}, status=400)

                try:
                    order = Order.objects.get(order_number=order_number, phone=phone_number, is_ordered=False)
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

                return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Payment not successful"})

        except Exception as e:
            print("Mpesa Callback Error:", str(e))
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Failed"}, status=400)
    else:
        return HttpResponse("Mpesa callback endpoint.", status=200)