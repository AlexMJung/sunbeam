from flask import Blueprint, render_template, url_for, session, redirect, request
from app import app
import os
import models
from oauth2client.client import OAuth2Credentials # gsuite
import httplib2
from apiclient import discovery
from app.authorize_qbo_blueprint.models import qbo

blueprint = Blueprint(os.path.dirname(os.path.realpath(__file__)).split("/")[-1], __name__, template_folder='templates', static_folder='static')

@blueprint.route("/", defaults={'id': app.config['GSUITE_CHARTS_OF_ACCOUNTS_FOLDER_ID']})
@blueprint.route("/<string:id>")
def index(id):
    if 'gsuite_credentials' not in session:
        return redirect(url_for("authorize_gsuite_blueprint.index", redirect_url=request.url))
    credentials = OAuth2Credentials.from_json(session['gsuite_credentials'])
    if credentials.access_token_expired:
        return redirect(url_for("authorize_gsuite_blueprint.index", redirect_url=request.url))
    http_auth = credentials.authorize(httplib2.Http())
    drive = discovery.build('drive', 'v3', http_auth)
    files = drive.files().list(q="'{0}' in parents and (mimeType='application/vnd.google-apps.spreadsheet' or mimeType='application/vnd.google-apps.folder')".format(id), orderBy="name").execute()['files']
    return render_template('charts_of_accounts.html', files = files, blueprint_name = blueprint.name)

@blueprint.route("/set_chart_of_accounts/<string:sheet_id>")
def set_chart_of_accounts(sheet_id):
    session['sheet_id'] = sheet_id
    return redirect(url_for("authorize_qbo_blueprint.index", redirect_url=url_for("{0}.update_chart_of_accounts".format(blueprint.name))))

@blueprint.route("/update_chart_of_accounts")
def update_chart_of_accounts():
    models.update_chart_of_accounts(qbo, session['qbo_company_id'], OAuth2Credentials.from_json(session['gsuite_credentials']), session['sheet_id'])
    return render_template('update_chart_of_accounts.html')
