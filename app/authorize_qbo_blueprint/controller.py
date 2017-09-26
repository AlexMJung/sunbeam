from flask import Blueprint, url_for, request, session, redirect
from app import app
import os
from requests_oauthlib import OAuth2Session
import models

blueprint = Blueprint(os.path.dirname(os.path.realpath(__file__)).split("/")[-1], __name__, template_folder='templates', static_folder='static')

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
qbo = OAuth2Session(
    app.config['QBO_CLIENT_ID'],
    scope = ['com.intuit.quickbooks.accounting', 'com.intuit.quickbooks.payment']
)

@blueprint.route("/")
def index():
    session['redirect_url'] = request.args.get("redirect_url")
    qbo.redirect_uri = url_for("{0}.authorized".format(blueprint.name), _external=True)
    authorization_url, _ = qbo.authorization_url("https://appcenter.intuit.com/connect/oauth2")
    return redirect(authorization_url)

@blueprint.route("/authorized")
def authorized():
    tokens = qbo.fetch_token(
        'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
        authorization_response = request.url,
        client_secret = app.config['QBO_CLIENT_SECRET']
    )
    company_id = request.args.get('realmId')
    session['qbo_company_id'] = company_id
    models.QBO(company_id).save_tokens(tokens)
    if session['redirect_url']:
        return redirect(session['redirect_url'])
    else:
        return "OK"
