import requests
from datetime import datetime
import json
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .generateAcesstoken import get_access_token
from .models import Order

@csrf_exempt
def initiate_stk_push(request):
    # Get access token
    access_token_response = get_access_token(request)
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if not access_token:
            return JsonResponse({'error': 'Access token not found.'})

        # Fetch the exact amount from the order
        try:
            order = Order.objects.get(user=request.user)
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

        # Prepare STK Push parameters
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        business_short_code = '174379'
        process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        callback_url = 'https://kariukijames.com/callback'
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
        account_reference = 'MAMAMAASAIBAKES'
        transaction_desc = f'Payment of order {order_number}'

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