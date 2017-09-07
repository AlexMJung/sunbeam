from flask import Blueprint, url_for, request, session, redirect
from app import app
import os
from models import qbo

blueprint = Blueprint(os.path.dirname(os.path.realpath(__file__)).split("/")[-1], __name__, template_folder='templates', static_folder='static')

@blueprint.route("/")
def index():
    session['redirect_url'] = request.args.get("redirect_url")
    return qbo.authorize(callback=url_for("{0}.authorized".format(blueprint.name), _external=True))

@blueprint.route("/authorized")
def authorized():
    qbo_tokens = qbo.authorized_response()
    qbo_company_id = request.args.get('realmId')
    qbo.store_authentication_tokens(qbo_tokens, qbo_company_id)
    qbo.authenticate_as(qbo_company_id)
    return redirect(session['redirect_url'])
