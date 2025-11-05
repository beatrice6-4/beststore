import requests
import json
import base64
from datetime import datetime
from django.http import JsonResponse
from .generateAcesstoken import get_access_token

def query_stk_status(request):
    access_token = get_access_token()
    if not access_token:
        return JsonResponse({'error': 'Access token not found.'})

    # LIVE endpoint and credentials
    query_url = 'https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query'
    business_short_code = '6391014'  # LIVE shortcode
    passkey = "46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933"  # LIVE passkey
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

    # Get CheckoutRequestID from POST or GET
    checkout_request_id = request.POST.get('CheckoutRequestID') or request.GET.get('CheckoutRequestID')
    if not checkout_request_id:
        return JsonResponse({'error': 'CheckoutRequestID is required.'})

    query_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    query_payload = {
        'BusinessShortCode': business_short_code,
        'Password': password,
        'Timestamp': timestamp,
        'CheckoutRequestID': checkout_request_id
    }

    try:
        response = requests.post(query_url, headers=query_headers, json=query_payload)
        response.raise_for_status()
        response_data = response.json()

        # Interpret common result codes
        result_code = str(response_data.get('ResultCode', ''))
        if result_code == '1037':
            message = "Timeout in completing transaction"
        elif result_code == '1032':
            message = "Transaction has been canceled by the user"
        elif result_code == '1':
            message = "The balance is insufficient for the transaction"
        elif result_code == '0':
            message = "The transaction was successful"
        else:
            message = f"Unknown result code: {result_code}"

        return JsonResponse({'message': message, 'response': response_data})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': 'Network error: ' + str(e)})
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Error decoding JSON: ' + str(e)})