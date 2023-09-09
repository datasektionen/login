from flask import Flask, request, redirect, abort, url_for, session, jsonify
from urllib.parse import urlencode
from authlib.integrations.flask_client import OAuth

from database import Database
import kth_ldap
import pls_api
import os
import secrets
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

app.config["KTH_CLIENT_ID"] = os.environ["CLIENT_ID"]
app.config["KTH_CLIENT_SECRET"] = os.environ["CLIENT_SECRET"]

oauth = OAuth(app)
oauth.register('kth',     
    server_metadata_url='https://login.ug.kth.se/adfs/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'})

LOGOUT_REDIRECT_URL = "https://datasektionen.se"

@app.route("/hello")
def hello():
    return "Hello Login!!!"

def valid_callback(callback_url):
    if os.environ.get('DONT_VALIDATE_CALLBACK', '0') != '0':
        return True
    return re.fullmatch("^https?://(([a-zA-Z0-9\-]+[.])*((datasektionen)|(dsekt)|(d-?dagen)|([bm]etaspexet))[.]se|localhost|127\.0\.0\.1)(:[1-9][0-9]*)?/.*$", callback_url) is not None

def upgrade_to_https(url):
    if url.startswith("https://"):
        return url
    if re.fullmatch("https?://(localhost|127\.0\.0\.1)(:[1-9][0-9]*)?/.*$", url):
        return url
    if not url.startswith("http://"):
        raise ValueError("Invalid url")
    return "https" + url[4:]
    
@app.route("/login")
def login():
    callback_url = request.args.get('callback')
    if not callback_url or not valid_callback(callback_url):
        return abort(400)
    try:
        session["DATA_CALLBACK"] = upgrade_to_https(callback_url)
    except ValueError:
        return abort(400)
    
    redirect_uri = url_for('callback', _external=True)
    redirect_uri = "https" + redirect_uri[4:]
    return oauth.kth.authorize_redirect(redirect_uri)

@app.route("/oidc/kth/callback")
def callback():
    try:
        token = oauth.kth.authorize_access_token()
        print(token)
        print("reeee")
    except Exception as e:
        print("error:", e)
        return abort(400)
    user_info = oauth.kth.parse_id_token(token)
    kthid = user_info.email

    callback = session["DATA_CALLBACK"]
    if not callback or not valid_callback(callback):
       return abort(400)
    db = Database()
    data_token = db.token_by_kthid(kthid)
    if data_token:
        db.update_time_created(data_token)
    else:
        db.delete_tokens(kthid)
        data_token = db.new_token(kthid)
    session["DATA_TOKEN"] = data_token

    return redirect(callback + data_token)

@app.route("/logout")
def logout():
    try:
        token = session["DATA_TOKEN"]
    except Exception as e:
        return redirect(LOGOUT_REDIRECT_URL)
    db = Database()
    db.delete_token(token)
    del session["DATA_TOKEN"]
    
    try:
        callback = request.headers["Referer"]
    except Exception as e:
        return redirect(LOGOUT_REDIRECT_URL)
    if not callback or not valid_callback(callback):
       return redirect(LOGOUT_REDIRECT_URL)
    return redirect(callback)

@app.route("/verify/<string:token>")
def verify(token):
    api_key = request.values.get('api_key')
    if not api_key:
        abort(400)

    db = Database()
    # db.api_key_exists is the old way of verifying API keys.
    # All new applications should instead use PLS API keys.
    if not (db.api_key_exists(api_key) or pls_api.verify(api_key)):
        abort(401)

    if token.endswith('.json'):
        token = token[:-5]
    kthid = db.kthid_by_token(token)

    if not kthid:
        abort(404)
    db.update_time_created(token)
    user_info = kth_ldap.get_user_info(kthid)
    # user_info = 
    if user_info:
        return  jsonify(user_info)
    else:
        abort(404)
