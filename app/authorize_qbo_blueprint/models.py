from flask import session, url_for
from app import app, db
import os
from requests_oauthlib import OAuth2Session
import datetime

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

class QBO():
    def __init__(self, company_id):
        self.company_id = company_id;

    def save_tokens(self, tokens):
        authorization_tokens = AuthenticationTokens.query.filter_by(company_id=self.company_id).first()
        if authorization_tokens is None:
            authorization_tokens = AuthenticationTokens(company_id=session['qbo_company_id'])
        authorization_tokens.access_token = tokens['access_token']
        authorization_tokens.refresh_token = tokens['refresh_token']
        db.session.add(authorization_tokens)
        db.session.commit()

    def client(self):
        authorization_tokens = AuthenticationTokens.query.filter_by(company_id=self.company_id).first()
        if authorization_tokens:
            client = OAuth2Session(
                app.config['QBO_CLIENT_ID'],
                token = {
                    'access_token': authorization_tokens.access_token,
                    'refresh_token': authorization_tokens.refresh_token,
                    'token_type': 'Bearer',
                    'expires_in': 3600 - (datetime.datetime.now() - authorization_tokens.date_modified).total_seconds()
                },
                auto_refresh_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
                auto_refresh_kwargs = {
                    'client_id': app.config['QBO_CLIENT_ID'],
                    'client_secret': app.config['QBO_CLIENT_SECRET']
                },
                token_updater = self.save_tokens
            )
            return client
        return None
