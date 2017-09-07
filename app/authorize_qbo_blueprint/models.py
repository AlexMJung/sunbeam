from flask import session
from app import app, db
import os
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials # gsuite
import httplib2
from apiclient import discovery
from flask_oauthlib.client import OAuth # qbo

tablename_prefix = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class Base(db.Model):
    __abstract__  = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class AuthenticationTokens(Base):
    __tablename__ = "{0}_authentication_tokens".format(tablename_prefix)
    company_id = db.Column(db.BigInteger)
    access_token = db.Column(db.String(1024))
    refresh_token = db.Column(db.String(120))

qbo = OAuth().remote_app(
    'qbo',
    consumer_key         = app.config['QBO_CLIENT_ID'],
    consumer_secret      = app.config['QBO_CLIENT_SECRET'],
    request_token_url    = None,
    request_token_params = {'scope': 'com.intuit.quickbooks.accounting com.intuit.quickbooks.payment', 'state': 'none'}, # state param required by Intuit
    access_token_method  = 'POST',
    authorize_url     = 'https://appcenter.intuit.com/connect/oauth2',
    access_token_url='https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
)

@qbo.tokengetter
def tokengetter():
    return (AuthenticationTokens.query.filter_by(company_id=session['qbo_company_id']).first().access_token, '')

def authenticate_as(company_id):
    session['qbo_company_id'] = company_id;
qbo.authenticate_as = authenticate_as

def store_authentication_tokens(tokens, company_id):
    authorization_tokens = AuthenticationTokens.query.filter_by(company_id=company_id).first()
    if authorization_tokens is None:
        authorization_tokens = AuthenticationTokens(company_id=company_id)
    authorization_tokens.access_token = tokens['access_token']
    authorization_tokens.refresh_token = tokens['refresh_token']
    db.session.add(authorization_tokens)
    db.session.commit()
qbo.store_authentication_tokens = store_authentication_tokens
