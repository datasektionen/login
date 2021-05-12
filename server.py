import flask
from flask import Flask, request, redirect, abort, url_for, session, jsonify
from flask_cas import CAS
from flask_cas import login as cas_login
from flask_cas import logout as cas_logout
from urllib.parse import urlencode

from database import Database
import kth_ldap
import pls_api
import os
import secrets
import re

app = Flask(__name__)
cas = CAS(app, '/cas')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(20))

app.config['CAS_SERVER'] = os.environ.get('CAS_SERVER', 'https://login.kth.se')
app.config['CAS_LOGIN_ROUTE'] = os.environ.get('CAS_LOGIN_ROUTE', '/p3/login')
app.config['CAS_LOGOUT_ROUTE'] = os.environ.get('CAS_LOGOUT_ROUTE', '/p3/logout')
app.config['CAS_VALIDATE_ROUTE'] = os.environ.get('CAS_VALIDATE_ROUTE', '/p3/serviceValidate')
app.config['CAS_AFTER_LOGIN'] = 'index'
app.debug = True

@app.route("/hello")
def hello():
    return "Hello Login!!!"

def valid_callback(callback_url):
    if os.environ.get('DONT_VALIDATE_CALLBACK', '0') != '0':
        return True
    return re.fullmatch("^https?://([a-zA-Z0-9]+[.])*datasektionen[.]se(:[1-9][0-9]*)?/.*$", callback_url) is not None

def upgrade_to_https(url):
    if url.startswith("https://"):
        return url
    if not url.startswith("http://"):
        raise ValueError("Invalid url")
    return "https" + url[4:]
    
@app.route("/login")
def login():
    callback_url = request.args.get('callback')
    if not callback_url or not valid_callback(callback_url):
        return abort(400)
    if 'CAS_USERNAME' not in flask.session:
        try:
            flask.session['CAS_AFTER_LOGIN_SESSION_URL'] = upgrade_to_https(flask.request.url)
        except ValueError:
            return abort(400)
        return cas_login()
    kthid = cas.username
    db = Database()
    token = db.token_by_kthid(kthid)
    if token:
        db.update_time_created(token)
    else:
        db.delete_tokens(kthid)
        token = db.new_token(kthid)

    return redirect(callback_url + token)

@app.route("/logout")
def logout():
    if 'CAS_USERNAME' not in flask.session:
        abort(400)
    kthid = cas.username
    db = Database()
    db.delete_tokens(kthid)
    return cas_logout()

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
    if user_info:
        return  jsonify(user_info)
    else:
        abort(404)
