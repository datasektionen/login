import flask
from flask import Flask, request, redirect, abort, url_for, session, jsonify
from flask_cas import CAS
from urllib.parse import urlencode

from database import Database
import kth_ldap

app = Flask(__name__)
cas = CAS(app, '/cas')
#app.config['SERVER_NAME'] = 'login.datasektionen.se'
app.config['SECRET_KEY'] = 'SOMETHINGSUPERDUP33RSECREET'

app.config['CAS_SERVER'] = 'https://login.kth.se'
app.config['CAS_LOGIN_ROUTE'] = '/p3/login'
app.config['CAS_LOGOUT_ROUTE'] = '/p3/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/p3/serviceValidate'
app.config['CAS_AFTER_LOGIN'] = 'index'


@app.route("/login")
def login():
    callback_url = request.args.get('callback')
    if not callback_url:
        abort(400)
    if 'CAS_USERNAME' not in flask.session:
        flask.session['CAS_AFTER_LOGIN_SESSION_URL'] = flask.request.url
        return redirect(flask.url_for('cas.login', _external=True))
    kthid = cas.username
    db = Database()
    token = db.token_by_kthid(kthid)
    if not token:
        token = db.new_token(kthid)
    return redirect(callback_url + '/' + token)


@app.route("/logout")
def logout():
    return redirect("http://login.kth.se/logout")

@app.route("/verify/<string:token>")
def verify(token):
    api_key = request.args.get('api_key')
    if not api_key:
        abort(400)

    db = Database()
    if not db.api_key_exists(api_key):
        abort(401)

    if token.endswith('.json'):
        token = token[:-5]
    kthid = db.kthid_by_token(token)

    if not kthid:
        abort(404)

    user_info = kth_ldap.get_user_info(kthid)
    if user_info:
        return  jsonify(user_info)
    else:
        abort(404)

# if __name__ == '__main__':
#    app.run(host='localhost.datasektionen.se', port=80)
