import unittest
import models
import flask
from app import app, db
import os
from app.authorize_qbo_blueprint.models import QBO, AuthenticationTokens
from random import randint
import uuid
import requests

blueprint_name = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class TestCase(unittest.TestCase):
    def setUp(self):
        company_id = AuthenticationTokens.query.first().company_id
        self.qbo = QBO(company_id).client()
        self.customer_id = self.qbo.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20customer&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], company_id), headers={'Accept': 'application/json'}).json()['QueryResponse']['Customer'][0]['Id']

    def test_save_bank_account(self):
        with app.test_request_context():
            models.BankAccount(customer_id=self.customer_id, name="Name", routing_number="121042882", account_number=str(randint(1000, 99999999999999999)), account_type="PERSONAL_CHECKING", phone="6128675309").save(self.qbo)

    def test_credit_card(self):
        with app.test_request_context():
            # don't use QBO client - this API does not - can not - have auth
            res = requests.post(
                "{0}/quickbooks/v4/payments/tokens".format(app.config["QBO_PAYMENTS_API_BASE_URL"]),
                headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot', 'Request-Id': str(uuid.uuid1())},
                json={
                    "card": {
                        "expYear": "2020",
                        "expMonth": "02",
                        "address": {
                          "region": "CA",
                          "postalCode": "94086",
                          "streetAddress": "1130 Kifer Rd",
                          "country": "US",
                          "city": "Sunnyvale"
                        },
                        "name": "emulate=0",
                        "cvc": "123",
                        "number": "4111111111111111"
                    }
                }
            )
            token = res.json()['value']
            models.CreditCard(customer_id=self.customer_id, token=token).save(self.qbo)
