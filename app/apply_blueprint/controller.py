
from flask import Blueprint, render_template, request, redirect, jsonify
import models
from app import app, db
import os
from flask_mail import Message
import traceback
from flask_cors import CORS, cross_origin

blueprint_name = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]
blueprint = Blueprint(blueprint_name, __name__, template_folder='templates', static_folder='static')

app.jinja_env.add_extension('jinja2.ext.do')

@blueprint.errorhandler(500)
def five_hundred(e):
    models.mail.send(
        Message(
            "500 - URL: {0} Error: {1}".format(request.url, e),
            sender="Wildflower Schools <noreply@wildflowerschools.org>",
            recipients=['dan.grigsby@wildflowerschools.org'],
            body=traceback.format_exc()
        )
    )
    return render_template('500.html', layout="{0}_layout.html".format(blueprint_name.rsplit('_', 1)[0]))

@blueprint.route('/redirect_to_survey_monkey_with_guid')
def redirect_to_survey_monkey_with_guid():
    hub = request.args.get("hub")
    return render_template('redirect_to_survey_monkey_with_guid.html', hub=hub, SURVEY_MONKEY_COLLECTOR_ID=app.config['HUBS'][hub.upper()]['SURVEY_MONKEY_COLLECTOR_ID'])

@blueprint.route('/after_survey_monkey')
def after_survey_monkey():
    response = models.SurveyMonkey.Response(request.args.get("hub"), guid=request.args.get("response_guid"))
    application = models.Application(response)
    application.submit_to_transparent_classroom()
    application.email_schools()
    application.email_parent()
    return render_template('after_survey_monkey.html', application=application)

@blueprint.route('/email_template')
@cross_origin()
def email_template():
    tc_school_id = request.args.get("tc_school_id")
    if tc_school_id:
        school = models.School.query.filter_by(tc_school_id=tc_school_id).first()
        return redirect(school.email_template_get_url())
    else:
        return redirect(models.School.default_email_template_get_url())

@blueprint.route('/email_template_post_parameters')
@cross_origin()
def email_template_post_parameters():
    tc_api_token = request.args.get("tc_api_token")
    tc_school_id = int(request.args.get("tc_school_id"))
    if models.TransparentClassroom.authorized(tc_api_token, tc_school_id):
        school = models.School.query.filter_by(tc_school_id=tc_school_id).first()
        return jsonify(school.email_template_post_parameters())
    return 401
