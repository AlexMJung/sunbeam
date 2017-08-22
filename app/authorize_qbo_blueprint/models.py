from flask import session
from app import app, db
import os
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials # gsuite
import httplib2
from apiclient import discovery
from flask_oauthlib.client import OAuth # qbo

print app.config

qbo = OAuth().remote_app(
    'qbo',
    request_token_url = 'https://oauth.intuit.com/oauth/v1/get_request_token',
    access_token_url  = 'https://oauth.intuit.com/oauth/v1/get_access_token',
    authorize_url     = 'https://appcenter.intuit.com/Connect/Begin',
    consumer_key      = "TMP", # app.config['QBO_CONSUMER_KEY'],
    consumer_secret   = "TMP" # app.config['QBO_CONSUMER_SECRET']
)

@qbo.tokengetter
def tokengetter():
    return session['qbo_tokens']['oauth_token'], session['qbo_tokens']['oauth_token_secret']

def authenticate_as(company_id):
    authorization_tokens = AuthenticationTokens.query.filter_by(company_id=company_id).first()
    session['qbo_tokens'] = {'oauth_token': authorization_tokens.oauth_token, 'oauth_token_secret': authorization_tokens.oauth_token_secret}
qbo.authenticate_as = authenticate_as


tablename_prefix = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class Base(db.Model):
    __abstract__  = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class AuthenticationTokens(Base):
    __tablename__ = "{0}_authentication_tokens".format(tablename_prefix)
    company_id = db.Column(db.BigInteger)
    oauth_token = db.Column(db.String(120))
    oauth_token_secret = db.Column(db.String(120))

def store_authentication_tokens(tokens, company_id):
    authorization_tokens = AuthenticationTokens.query.filter_by(company_id=company_id).first()
    if authorization_tokens is None:
        authorization_tokens = AuthenticationTokens(company_id=company_id)
    authorization_tokens.oauth_token = tokens['oauth_token']
    authorization_tokens.oauth_token_secret = tokens['oauth_token_secret']
    db.session.add(authorization_tokens)
    db.session.commit()
