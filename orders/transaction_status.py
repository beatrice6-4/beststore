import requests
from datetime import datetime
import base64
from .generateAcesstoken import get_access_token

def check_transaction_status(transaction_id):
    access_token = get_access_token()
    if not access_token:
        return {'error': 'Access token not found.'}

    url = 'https://api.safaricom.co.ke/mpesa/transactionstatus/v1/query'
    business_short_code = '3581517'  # Your Paybill
    initiator = 'BWANYONYI'
    security_credential = 'Bramwel,wanyo2001'
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    passkey = '46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933'
    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

    payload = {
        "Initiator": initiator,
        "SecurityCredential": security_credential,
        "CommandID": "TransactionStatusQuery",
        "TransactionID": transaction_id,
        "PartyA": business_short_code,
        "IdentifierType": "4",  # 4 for Paybill, 2 for Till
        "ResultURL": "https://mamamaasaibakers.com/mpesa/transaction/result/",
        "QueueTimeOutURL": "https://mamamaasaibakers.com/mpesa/transaction/timeout/",
        "Remarks": "Checking transaction status",
        "Occasion": "OrderStatus"
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': 'Network error: ' + str(e)}