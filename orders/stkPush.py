

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order
from .generateAcesstoken import get_access_token
import base64
import requests
from datetime import datetime
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
                if phone_number.startswith("+"):
                    phone_number = phone_number[1:]
                if phone_number.startswith("0"):
                    phone_number = "254" + phone_number[1:]
                if not phone_number.startswith("254") or len(phone_number) != 12:
                    payment_response = {'error': 'Invalid phone number format. Use 2547XXXXXXXX.'}
                else:
                    passkey = "46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933"  # LIVE passkey
                    business_short_code = '3581517'  # LIVE shortcode
                    process_request_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'  # LIVE endpoint
                    callback_url = 'https://mamamaasaibakers.com/orders/mpesa/callback/'
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
                    transaction_desc = f'Payment for Order {order_number}'
                    account_reference = f'{phone_number} {order_number}'
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


def initiate_stk_push(phone_number, amount, order_number):
    access_token = get_access_token()
    if not access_token:
        return {'error': 'Access token not found.'}

    # Format phone number
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]
    if phone_number.startswith("0"):
        phone_number = "254" + phone_number[1:]
    if not phone_number.startswith("254") or len(phone_number) != 12:
        return {'error': 'Invalid phone number format. Use 2547XXXXXXXX.'}

    passkey = "46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933"  # LIVE passkey
    business_short_code = '3581517'  # LIVE shortcode
    process_request_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'  # LIVE endpoint
    callback_url = 'https://mamamaasaibakers.com/orders/mpesa/callback/'
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
    transaction_desc = f'Payment for Order {order_number}'
    account_reference = f'{phone_number} {order_number}'

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
        return response_data
    except requests.exceptions.RequestException as e:
        return {'error': 'Failed to initiate STK Push.', 'details': str(e)}