from flask import Blueprint
import os

blueprint_name = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]
blueprint = Blueprint(blueprint_name, __name__, template_folder='templates', static_folder='static')

@blueprint.errorhandler(500)
def five_hundred(e):
    models.mail.send(
        Message(
            "500 - URL: {0} Error: {1}".format(request.url, e),
            sender="Wildflower Schools <noreply@wildflowerschools.org>",
            recipients=['support@wildflowerschools.org'],
            body=traceback.format_exc()
        )
    )
    return render_template('500.html', layout="{0}_layout.html".format(blueprint_name.rsplit('_', 1)[0]))
