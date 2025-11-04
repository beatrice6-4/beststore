import requests

def get_access_token():
    consumer_key = "kfy4wKPlLpC4AGlZRphJl1VgpzAVc1fNVs4w2l3vNVb1GuqM"
    consumer_secret = "4TgAMbmpG5wbH4mqFpIYZ6tOCGFWGnJjMBvFE7Z4DobFfcJjmvDjLnsWcoIm9FLf"
    url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    access_token = response.json()['access_token']
    return access_token