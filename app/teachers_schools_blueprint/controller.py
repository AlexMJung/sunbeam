from apiclient import discovery
from app import app
from flask import Blueprint, request
import json
from oauth2client.service_account import ServiceAccountCredentials
import os

from lib.google_drive_service import GDriveService, MissingFolderError, FolderAlreadyExistsError

blueprint = Blueprint(os.path.dirname(os.path.realpath(__file__)).split("/")[-1], __name__, template_folder='templates', static_folder='static')
GSUITE_SCOPES = ['https://www.googleapis.com/auth/drive']


def gsuite_credentials():
    return ServiceAccountCredentials.from_json_keyfile_dict(
        keyfile_dict=json.loads(app.config['GSUITE_SERVICE_ACCOUNT_CREDENTIALS']),
        scopes=GSUITE_SCOPES
    )


def new_drive_service():
    """
    Build Google Drive service using delegated credentials
    """
    credentials = gsuite_credentials()
    delegated_credentials = credentials.create_delegated('ben.talberg@wildflowerschools.org')
    drive = discovery.build('drive', 'v3', credentials=delegated_credentials)

    return GDriveService(
        drive=drive,
        templates_folder_id=app.config['TEACHERS_SCHOOLS_TEMPLATES_FOLDER_ID'],
        live_folder_id=app.config['TEACHERS_SCHOOLS_LIVE_FOLDER_ID']
    )


def teacher_school_create_handler(template_type):
    post = request.get_json()
    if 'name' not in post:
        return "'name' required", 422

    name = post['name']
    if name is None or name.strip() == "":
        return "'name' must not be empty", 422

    try:
        drive = new_drive_service()
        drive.replicate_template(template_type, name)
    except MissingFolderError as e:
        return e.message, 400
    except FolderAlreadyExistsError as e:
        return e.message, 409
    except ValueError as e:
        app.logger.error(e.message)
        return e.message, 500
    except Exception as e:
        app.logger.error(e.message)
        return '', 500

    return ''


@blueprint.route('/teachers', methods=['POST'])
def teacher():
    return teacher_school_create_handler('teacher')


@blueprint.route('/schools', methods=['POST'])
def school():
    return teacher_school_create_handler('school')
