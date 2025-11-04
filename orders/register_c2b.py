import requests
from .generateAcesstoken import get_access_token

def register_c2b_urls():
    access_token = get_access_token()
    url = 'https://api.safaricom.co.ke/mpesa/c2b/v1/registerurl'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "ShortCode": "3581517",  # Your Paybill/Till
        "ResponseType": "Completed",
        "ConfirmationURL": "https://mamamaasaibakers.com/mpesa/confirmation/",
        "ValidationURL": "https://mamamaasaibakers.com/mpesa/validation/"
    }
    response = requests.post(url, headers=headers, json=payload)
    print(response.json())