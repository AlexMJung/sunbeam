from flask import Blueprint, url_for, request, session, redirect
from app import app
import os
from models import qbo, store_authentication_tokens, authenticate_as

blueprint = Blueprint(os.path.dirname(os.path.realpath(__file__)).split("/")[-1], __name__, template_folder='templates', static_folder='static')

@blueprint.route("/")
def index():
    session['redirect_url'] = request.args.get("redirect_url")
    return qbo.authorize(callback=url_for("{0}.authorized".format(blueprint.name), _external=True))

@blueprint.route("/authorized")
def authorized():
    qbo_company_id = request.args.get('realmId')
    authenticate_as(qbo_company_id)
    qbo_tokens = qbo.authorized_response()
    store_authentication_tokens(qbo_tokens)
    if session['redirect_url']:
        return redirect(session['redirect_url'])
    else:
        return "OK"
