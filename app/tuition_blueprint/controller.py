from flask import Blueprint
import os
import models
from flask_cors import CORS, cross_origin

blueprint = Blueprint(os.path.dirname(os.path.realpath(__file__)).split("/")[-1], __name__, template_folder='templates', static_folder='static')


# XXX TODO !!! NEXT DO AUTHENTICATION


@blueprint.route('/customers')
@cross_origin()
def customers():
    return "TBD"

@blueprint.route('/recurring_payments', methods=['GET', 'POST'])
@cross_origin()
def recurring_payments():
    return "TBD"

@blueprint.route('/recurring_payments/<int:recurring_payment_id>', methods=['DELETE'])
@cross_origin()
def delete_recurring_payment(recurring_payment_id):
    return "TBD"

@blueprint.route('/items')
@cross_origin()
def items():
    return "TBD"
