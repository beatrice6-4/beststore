from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
                    passkey = "46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933"
                    business_short_code = '3581517'
                    process_request_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
                    callback_url = 'https://mamamaasaibakers.com/orders/mpesa/callback/'
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
                    transaction_desc = f'Payment for Order {order_number}'
                    account_reference = f'Order-{order_number}'
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