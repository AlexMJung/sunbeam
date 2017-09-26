from flask import Blueprint, session, redirect, url_for, request
import os
import models
from flask_cors import CORS, cross_origin
from app.authorize_qbo_blueprint.models import QBO
from app import db

blueprint = Blueprint(os.path.dirname(os.path.realpath(__file__)).split("/")[-1], __name__, template_folder='templates', static_folder='static')

@blueprint.route('/')
def index():
    if not session.get('qbo_company_id', None):
        return redirect(url_for("authorize_qbo_blueprint.index", redirect_url=url_for("{0}.index".format(blueprint.name))))
    return "OK"

@blueprint.route('/customers')
@cross_origin()
def customers():
    return models.CustomerSchema(many=True).jsonify(
        models.Customer.customers_from_qbo(session['qbo_company_id'], QBO(session['qbo_company_id']).client())
    )

@blueprint.route('/recurring_payments', methods=['GET', 'POST'])
@cross_origin()
def recurring_payments():
    if request.method == 'GET':
        return models.RecurringPaymentSchema(many=True).jsonify(
            models.RecurringPayment.query.filter_by(company_id=session['qbo_company_id']).all()
        )
    elif request.method == 'POST':
        return "TBD"

@blueprint.route('/recurring_payments/<int:recurring_payment_id>', methods=['DELETE', 'GET'])
@cross_origin()
def delete_recurring_payment(recurring_payment_id):
    recurring_payment = models.RecurringPayment.query.filter_by(company_id=session['qbo_company_id']).filter_by(id='recurring_payment_id').first()
    db.session.delete(recurring_payment)
    db.session.commit()
    return ('', 204)

@blueprint.route('/items')
@cross_origin()
def items():
    return models.ItemSchema(many=True).jsonify(
        models.Item.items_from_qbo(session['qbo_company_id'], QBO(session['qbo_company_id']).client())
    )
