import requests
import base64
from datetime import datetime
from .generateAcesstoken import get_access_token

def query_account_balance():
    access_token = get_access_token()
    url = 'https://api.safaricom.co.ke/mpesa/accountbalance/v1/query'
    business_short_code = '3581517'  # Your Paybill/Till
    initiator = 'BWANYONYI'
    security_credential = 'Bramwel,wanyo2001'
    command_id = 'AccountBalance'
    party_a = business_short_code
    identifier_type = '4'  # 4 for Paybill, 2 for Till
    remarks = 'Balance check'
    queue_timeout_url = 'https://mamamaasaibakers.com/mpesa/balance/timeout/'
    result_url = 'https://mamamaasaibakers.com/mpesa/balance/result/'

    payload = {
        "Initiator": initiator,
        "SecurityCredential": security_credential,
        "CommandID": command_id,
        "PartyA": party_a,
        "IdentifierType": identifier_type,
        "Remarks": remarks,
        "QueueTimeOutURL": queue_timeout_url,
        "ResultURL": result_url
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()