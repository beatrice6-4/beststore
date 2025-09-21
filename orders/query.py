import requests
import json
import base64
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .generateAcesstoken import get_access_token

@csrf_exempt
def query_stk_status(request):
    """
    Query the status of an STK Push payment using CheckoutRequestID.
    Expects POST with 'checkout_request_id' in the body.
    """
    access_token_response = get_access_token(request)
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if not access_token:
            return JsonResponse({'error': 'Access token not found.'})

        if request.method == "POST":
            try:
                data = json.loads(request.body.decode('utf-8'))
                checkout_request_id = data.get('checkout_request_id')
                if not checkout_request_id:
                    return JsonResponse({'error': 'checkout_request_id is required.'})
            except Exception as e:
                return JsonResponse({'error': 'Invalid JSON body: ' + str(e)})
        else:
            return JsonResponse({'error': 'Invalid request method. Use POST.'})

        query_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
        business_short_code = '174379'
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

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

            result_code = response_data.get('ResultCode')
            result_desc = response_data.get('ResultDesc', 'No description provided.')

            # Interpret common result codes
            code_meanings = {
                '0': "Transaction successful",
                '1': "Insufficient balance",
                '1032': "Transaction canceled by user",
                '1037': "Timeout in completing transaction"
            }
            message = code_meanings.get(str(result_code), f"Unknown result code: {result_code}")

            return JsonResponse({
                'ResultCode': result_code,
                'ResultDesc': result_desc,
                'message': message,
                'response': response_data
            })
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'Network error: ' + str(e)})
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Error decoding JSON: ' + str(e)})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})
    