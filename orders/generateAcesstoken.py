import requests
from django.http import JsonResponse

def get_access_token():
    consumer_key = "kfy4wKPlLpC4AGlZRphJl1VgpzAVc1fNVs4w2l3vNVb1GuqM"  
    consumer_secret = "4TgAMbmpG5wbH4mqFpIYZ6tOCGFWGnJjMBvFE7Z4DobFfcJjmvDjLnsWcoIm9FLf"  
    access_token_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status() 
        result = response.json()
        access_token = result['access_token']
        return JsonResponse({'access_token': access_token})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Unknown error occurred.'})