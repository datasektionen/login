import requests
import string

API_KEY_ALPHABET = set(string.ascii_letters + string.digits + "-_=")

def valid_api_key(api_key):
    for c in api_key:
        if c not in API_KEY_ALPHABET:
            return False
    return True

def verify(api_key):
    if not valid_api_key(api_key):
        return False
    try:
        permissions = requests.get(f'https://pls.datasektionen.se/api/token/{api_key}/login/').json()
    except:
        return False
    return isinstance(permissions, list) and 'login' in permissions
