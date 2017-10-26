from flask import Blueprint, session, redirect, url_for, request, Response
import os
import models
from flask_cors import CORS, cross_origin
from app.authorize_qbo_blueprint.models import QBO
from app import db
import json
import re
from flask import jsonify
from functools import wraps

blueprint = Blueprint(os.path.dirname(os.path.realpath(__file__)).split("/")[-1], __name__, template_folder='templates', static_folder='static')

def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('qbo_company_id', None):
            return Response(response="{}", status=401, mimetype='application/json')
        else:
            return f(*args, **kwargs)

    return decorated_function

@blueprint.route('/')
def index():
    if not session.get('qbo_company_id', None):
        return redirect(url_for("authorize_qbo_blueprint.index", redirect_url=url_for("{0}.index".format(blueprint.name))))
    return redirect(url_for('static', filename='react/index.html'))

@blueprint.route('/customers')
@cross_origin(supports_credentials=True)
@requires_auth
def customers():
    success, value = models.Customer.customers_from_qbo(session['qbo_company_id'], QBO(session['qbo_company_id']).client())
    if not success:
        return Response(value, status=500, mimetype='application/json')
    customers = value
    return models.CustomerSchema(many=True).jsonify(customers)

def parse_existing_id_from_error(s):
    r = re.compile(".* id is ([0-9]+).")
    m = r.match(json.loads(s)["errors"][0]["detail"])
    if m and len(m.groups()) == 1:
        return m.group(1)
    return None

@blueprint.route('/bank_account', methods=['POST'])
@cross_origin(supports_credentials=True)
@requires_auth
def bank_account():
    qbo_client = QBO(session['qbo_company_id']).client()
    post = request.get_json()

    success, value = models.Customer.customer_from_qbo(session['qbo_company_id'], post['customer_id'], qbo_client)
    if not success:
        return Response(value, status=500, mimetype='application/json')
    customer = value

    bank_account = models.BankAccount(
        customer=customer,
        name=post['name'],
        routing_number=post['routing_number'],
        account_number=post['account_number'],
        phone=post['phone'],
        qbo_client=qbo_client
    )

    success, value = bank_account.save()
    if not success:
        id = parse_existing_id_from_error(value)
        if not id:
            return Response(value, status=500, mimetype='application/json')
        value = id

    return jsonify({'id': value})

@blueprint.route('/credit_card', methods=['POST'])
@cross_origin(supports_credentials=True)
@requires_auth
def credit_card():
    qbo_client = QBO(session['qbo_company_id']).client()
    post = request.get_json()

    success, value = models.Customer.customer_from_qbo(session['qbo_company_id'], post['customer_id'], qbo_client)
    if not success:
        return Response(value, status=500, mimetype='application/json')
    customer = value

    credit_card = models.CreditCard(
        customer=customer,
        token=post['token'],
        qbo_client=qbo_client
    )

    success, value = credit_card.save()
    if not success:
        print value
        id = parse_existing_id_from_error(value)
        if not id:
            return Response(value, status=500, mimetype='application/json')
        value = id

    return jsonify({'id': value})

@blueprint.route('/recurring_payments', methods=['POST'])
@cross_origin(supports_credentials=True)
@requires_auth
def recurring_payments():
    post = request.get_json()

    recurring_payment = models.RecurringPayment(
        company_id = session['qbo_company_id'],
        customer_id = post['customer_id'],
        bank_account_id = post.get('bank_account_id', None),
        credit_card_id = post.get('credit_card_id', None),
        item_id = post['item_id'],
        amount = post['amount'],
        start_date = post['start_date'],
        end_date = post['end_date']
    )

    db.session.add(recurring_payment)
    db.session.commit()

    return ('', 204)

@blueprint.route('/recurring_payments/<int:recurring_payment_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
@requires_auth
def delete_recurring_payment(recurring_payment_id):
    recurring_payment = models.RecurringPayment.query.filter_by(company_id=session['qbo_company_id']).filter_by(id=recurring_payment_id).first()
    db.session.delete(recurring_payment)
    db.session.commit()
    return ('', 204)

@blueprint.route('/items')
@cross_origin(supports_credentials=True)
@requires_auth
def items():
    success, value = models.Item.items_from_qbo(session['qbo_company_id'], QBO(session['qbo_company_id']).client())
    if not success:
        return Response(value, status=500, mimetype='application/json')
    items = value
    return models.ItemSchema(many=True).jsonify(items)
