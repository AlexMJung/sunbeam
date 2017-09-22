from flask import session, url_for
from app import app, db
import os
from requests_oauthlib import OAuth2Session
from datetime import datetime
import time

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


class OAuth2SessionWithRateLimit(OAuth2Session):
    def __init__(self, *args, **kwargs):
        self.last_api_call = None
        self.rate_limit = kwargs['rate_limit']
        del kwargs['rate_limit']
        super(OAuth2SessionWithRateLimit, self).__init__(*args, **kwargs)

    def request(self, method, url, **kwargs):
        if self.rate_limit:
            if self.last_api_call:
                seconds = (datetime.now() - self.last_api_call).total_seconds()
                if seconds < 60 / self.rate_limit:
                    sleep = 60 / self.rate_limit - seconds
                    app.logger.info("Enforcing rate limit by sleeping {0} seconds".format(sleep))
                    time.sleep(sleep)
            # I decided to record the last api call time before the request, instead of after
            # this is conservative, because the time to make the request is not included
            # I considered timing if from after the super call returns, but there is some
            # time spent on processing the result and, consequently, if you make a call
            # immediately thereafter it /could/ be too quick
            self.last_api_call = datetime.now()
        return super(OAuth2SessionWithRateLimit, self).request(method, url, **kwargs)

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

    def client(self, rate_limit=None):
        authorization_tokens = AuthenticationTokens.query.filter_by(company_id=self.company_id).first()
        if authorization_tokens:
            client = OAuth2SessionWithRateLimit(
                app.config['QBO_CLIENT_ID'],
                token = {
                    'access_token': authorization_tokens.access_token,
                    'refresh_token': authorization_tokens.refresh_token,
                    'token_type': 'Bearer',
                    'expires_in': 3600 - (datetime.now() - authorization_tokens.date_modified).total_seconds()
                },
                auto_refresh_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
                auto_refresh_kwargs = {
                    'client_id': app.config['QBO_CLIENT_ID'],
                    'client_secret': app.config['QBO_CLIENT_SECRET']
                },
                token_updater = self.save_tokens,
                rate_limit = rate_limit
            )
            return client
        return None
