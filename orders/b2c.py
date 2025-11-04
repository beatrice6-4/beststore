import requests
import base64
from datetime import datetime
from .generateAcesstoken import get_access_token

def b2c_payment_request(phone_number, amount, remarks="Payment"):
    access_token = get_access_token()
    url = 'https://api.safaricom.co.ke/mpesa/b2c/v3/paymentrequest'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "InitiatorName": "BRAMWEL,",
        "SecurityCredential": "123456",
        "CommandID": "BusinessPayment",  # or SalaryPayment, PromotionPayment
        "Amount": amount,
        "PartyA": "3581517",  # Your Paybill/Till
        "PartyB": phone_number,  # Customer's phone number
        "Remarks": remarks,
        "QueueTimeOutURL": "https://mamamaasaibakers.com/mpesa/b2c/timeout/",
        "ResultURL": "https://mamamaasaibakers.com/mpesa/b2c/result/",
        "Occasion": "Payment"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()