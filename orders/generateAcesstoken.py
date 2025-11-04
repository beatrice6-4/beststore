import requests

def get_access_token():
    consumer_key = "Y5yB22NEdfA7h1tEzr3d0bPKj2SG6p3v48wD9HgdBo8ABM0W"  
    consumer_secret = "rGAb1Ic3OcdyDtvHOUyjJiq301cjTiMmzczDPQTkG3T5YQrpZkfdrfL34p8CpPST"  
    access_token_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status() 
        result = response.json()
        access_token = result['access_token']
        return access_token
    except requests.exceptions.RequestException as e:
        print("Access token error:", str(e))
        return None