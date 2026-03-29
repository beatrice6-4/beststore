import requests

def get_access_token():
    # TODO: Replace these with your LIVE M-Pesa credentials from Safaricom Developer Portal
    # Get your credentials from: https://developer.safaricom.co.ke/apps
    consumer_key = "kfy4wKPlLpC4AGlZRphJl1VgpzAVc1fNVs4w2l3vNVb1GuqM"  # Replace with your live key
    consumer_secret = "4TgAMbmpG5wbH4mqFpIYZ6tOCGFWGnJjMBvFE7Z4DobFfcJjmvDjLnsWcoIm9FLf"  # Replace with your live secret
    url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        response = requests.get(url, auth=(consumer_key, consumer_secret), timeout=5)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            return access_token
        else:
            print(f"Token generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting access token: {str(e)}")
        return None