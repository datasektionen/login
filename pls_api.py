import requests

def verify(api_key):
    permissions = requests.get(f'https://pls.datasektionen.se/api/token/{api_key}/login/').json()
    return 'login' in permissions
