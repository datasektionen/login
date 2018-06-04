from flask import Flask, request, redirect, abort, url_for, session, jsonify
from flask_cas import CAS, login, login_required
from urllib.parse import urlencode

from database import Database


app = Flask(__name__)
cas = CAS(app, '/cas')
app.config['SERVER_NAME'] = 'localhost.datasektionen.se'
app.config['SECRET_KEY'] = 'SOMETHING'

app.config['CAS_SERVER'] = 'https://login.kth.se'
app.config['CAS_LOGIN_ROUTE'] = '/p3/login'
app.config['CAS_LOGOUT_ROUTE'] = '/p3/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/p3/serviceValidate'
app.config['CAS_AFTER_LOGIN'] = 'index'


@app.route("/login")
@login_required
def login():
    callback_url = request.args.get('callback')
    print(cas.attributes)
    print(cas.username)

    return "success"


@app.route("/logout")
def logout():
    redirect("http://login.kth.se/logout")

@app.route("/verify/<string:token>")
def verify(token):
    api_key= request.args.get('api_key')
    if not api_key:
        abort(400)

    db = Database()
    if not db.api_key_exists(api_key):
        abort(401)

    if token.endswith('.json'):
        token = token[:-5]
    ugid = db.ugid_by_token(token)
    if not ugid:
        abort(404)
    else:
        return jsonify({ 'ugkthid' : ugid })


if __name__ == '__main__':
    app.run(host='localhost.datasektionen.se', port=80)
