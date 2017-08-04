from flask import Blueprint, url_for, request, session, redirect
from app import app
import os
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials # gsuite

blueprint = Blueprint(os.path.dirname(os.path.realpath(__file__)).split("/")[-1], __name__, template_folder='templates', static_folder='static')

def flow():
    return OAuth2WebServerFlow(
        client_id=app.config['GSUITE_CLIENT_ID'],
        client_secret=app.config['GSUITE_CLIENT_SECRET'],
        scope='https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/spreadsheets.readonly',
        redirect_uri=url_for("{0}.authorized".format(blueprint.name), _external=True)
    )

@blueprint.route("/")
def index():
    session['redirect_url'] = request.args.get("redirect_url")
    return redirect(flow().step1_get_authorize_url())

@blueprint.route("/authorized")
def authorized():
    credentials = flow().step2_exchange(request.args.get('code'))
    session['gsuite_credentials'] = credentials.to_json()
    return redirect(session['redirect_url'])
