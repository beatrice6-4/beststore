import requests

def get_access_token():
    consumer_key = "kfy4wKPlLpC4AGlZRphJl1VgpzAVc1fNVs4w2l3vNVb1GuqM"
    consumer_secret = "4TgAMbmpG5wbH4mqFpIYZ6tOCGFWGnJjMBvFE7Z4DobFfcJjmvDjLnsWcoIm9FLf"
    access_token_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    try:
        response = requests.get(access_token_url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()
        result = response.json()
        return result.get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Access token error: {e}")
        return None